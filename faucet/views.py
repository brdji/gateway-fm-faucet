import datetime

from django.http import (
    HttpRequest,
    HttpResponseBadRequest,
    HttpResponseServerError,
    JsonResponse,
)
from django.shortcuts import render
from django.utils import timezone
from django.views.decorators.http import require_POST, require_GET

import faucet.chain as chain
from faucet.forms import FaucetRequestForm
from faucet.models import FaucetRequest
from gateway_faucet import settings

import logging

logger = logging.getLogger(__name__)

# Request to transfer funds from the pre-funded wallet to the given destination address
@require_POST
def faucet_fund(request: HttpRequest):
    resp_data = {}

    ip_address = request.get_host()

    # Validate sent data
    form = FaucetRequestForm(data=request.POST)
    dest_address = None
    if form.is_valid():
        cd = form.cleaned_data
        dest_address = cd["address"]
    else:
        return HttpResponseBadRequest(form.errors.as_json())
    
    logger.info(f'Received faucet fund request from IP = {ip_address}, to address = {dest_address}')

    if not _check_request_validity(request.get_host(), dest_address):
        return HttpResponseBadRequest("Too many recent fund requests, please wait")

    # Address validity check
    addr_valid = chain.validate_address(dest_address)
    if not addr_valid:
        return HttpResponseBadRequest("Invalid recipient address")

    # Wallet balance check
    can_send = chain.wallet_balance_check()
    if not can_send:
        return HttpResponseServerError("Insufficient faucet funds")

    # Prepare request to insert into DB
    faucet_request = FaucetRequest()
    faucet_request.ip_address = ip_address
    faucet_request.destination_address = dest_address
    
    # Execute transfer
    try:
        logger.info(f'Executing transfer to {dest_address}')
        tx_hash = chain.send_ETH(dest_address)
        resp_data["tx_hash"] = tx_hash
        faucet_request.tx_hash = tx_hash
    except Exception as e:
        logger.error(e)
        # Generally we shouldn't return server errors directly to clients
        # In this case, howerver, we need a "descriptive error" to signal what went wrong with the transaction
        return HttpResponseServerError(f"Error transferring funds: {e}")
    finally:
        # Insert request into DB
        faucet_request.save()

    logger.info(f'Sucessfully transferred funds to {dest_address}. TX hash: {tx_hash}')
    return JsonResponse(resp_data)


# Request to retrieve faucet stats for the past 24 hours
@require_GET
def list_fund_stats(request: HttpRequest):
    day_before = timezone.now() - datetime.timedelta(hours=24)
    fund_requests = FaucetRequest.objects.filter(created_on__gte=day_before)
    # We only need to count the failed requests; no need to filter the queryset twice
    failed = fund_requests.filter(tx_hash="").count()
    successful = fund_requests.count() - failed

    resp_data = {}
    resp_data["successful_txs"] = successful
    resp_data["failed_txs"] = failed
    return JsonResponse(resp_data)

# Checks if the request from the given IP address and to the specified destination address is valid
# If more than 1 request has been made in the predefined time period, the request is invalid
# Otherwise, it is valid
def _check_request_validity(ip_address: str, dest_address: str) -> bool:
    if ip_address is None or dest_address is None:
        return False
    minute_ago = timezone.now() - datetime.timedelta(
        seconds=settings.FAUCET_REQUEST_TIMEOUT_SECONDS
    )
    last_minute_requests = FaucetRequest.objects.filter(created_on__gte=minute_ago)

    same_ip_address_requests = last_minute_requests.filter(ip_address=ip_address)
    same_dest_address_requests = last_minute_requests.filter(
        destination_address=dest_address
    )

    if same_dest_address_requests.count() > 0 or same_ip_address_requests.count() > 0:
        return False
    return True
