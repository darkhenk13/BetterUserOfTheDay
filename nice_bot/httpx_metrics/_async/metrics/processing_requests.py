import httpx

from nice_bot.httpx_metrics.metrics_registry import HTTPX_CLIENT_PROCESSING_REQUESTS

from .base import AsyncBaseMetricTransport
import re

class AsyncProcessingRequestsMetric(AsyncBaseMetricTransport):
    async def handle_async_request(self, request: httpx.Request) -> httpx.Response:

        url = request.url.path
        pattern = r"^/bot[^/]+(.*)$"
        match = re.match(pattern, url)
        methods_res = match.group(1)

        HTTPX_CLIENT_PROCESSING_REQUESTS.labels(
            method=request.method,
            path=methods_res,
        ).inc()
        try:
            response = await self.next_transport.handle_async_request(request)
        finally:
            url = request.url.path
            pattern = r"^/bot[^/]+(.*)$"
            match = re.match(pattern, url)
            methods_res = match.group(1)
            HTTPX_CLIENT_PROCESSING_REQUESTS.labels(
                method=request.method,
                path=methods_res,
            ).dec()
        return response
