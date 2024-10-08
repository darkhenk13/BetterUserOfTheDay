import time

import httpx
import re
from nice_bot.httpx_metrics.metrics_registry import HTTPX_CLIENT_REQUESTS_DURATION_SECONDS

from .base import AsyncBaseMetricTransport


class AsyncRequestsDurationMetric(AsyncBaseMetricTransport):
    async def handle_async_request(self, request: httpx.Request) -> httpx.Response:
        t1 = time.monotonic()
        response = await self.next_transport.handle_async_request(request)
        t2 = time.monotonic()

        url = request.url.path
        pattern = r"^/bot[^/]+(.*)$"
        match = re.match(pattern, url)
        methods_res = match.group(1)

        HTTPX_CLIENT_REQUESTS_DURATION_SECONDS.labels(
            method=request.method,
            status_code=response.status_code,
            path=methods_res,
            version=response.extensions["http_version"],
        ).observe(t2 - t1)

        return response
