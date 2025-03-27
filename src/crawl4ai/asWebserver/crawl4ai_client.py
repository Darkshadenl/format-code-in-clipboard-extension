import requests
import time
from typing import Dict, List, Union, Optional


class Crawl4AIClient:
    def __init__(
        self, base_url: str = "http://localhost:11235", api_token: Optional[str] = None
    ):
        """
        Initialize the Crawl4AI client

        Args:
            base_url: The base URL of the Crawl4AI API
            api_token: Optional API token for authentication
        """
        self.base_url = base_url
        self.headers = {}
        if api_token:
            self.headers["Authorization"] = f"Bearer {api_token}"

    def health_check(self) -> Dict:
        """Check if the Crawl4AI service is healthy"""
        response = requests.get(f"{self.base_url}/health")
        return response.json()

    def crawl(
        self,
        urls: Union[str, List[str]],
        priority: int = 5,
        extraction_config: Optional[Dict] = None,
        crawler_params: Optional[Dict] = None,
        extra: Optional[Dict] = None,
        wait_for_completion: bool = True,
        timeout: int = 300,
        request: Optional[Dict] = None,
    ) -> Dict:
        """
        Submit a crawl job to Crawl4AI

        Args:
            urls: URL or list of URLs to crawl
            priority: Job priority (1-10)
            extraction_config: Configuration for content extraction
            crawler_params: Parameters for the crawler
            extra: Extra parameters for the crawler
            wait_for_completion: Whether to wait for the job to complete
            timeout: Timeout in seconds when waiting for completion

        Returns:
            The crawl result or task information
        """
        request_data = {"urls": urls, "priority": priority}

        if extraction_config:
            request_data["extraction_config"] = extraction_config

        if crawler_params:
            request_data["crawler_params"] = crawler_params

        if extra:
            request_data["extra"] = extra

        # Submit the crawl job
        if not request:
            response = requests.post(
                f"{self.base_url}/crawl", headers=self.headers, json=request_data
            )
        else:
            response = requests.post(
                f"{self.base_url}/crawl", headers=self.headers, json=request
            )

        if not response.ok:
            print(f"Error: {response.status_code}")
            print(response.text)
            return {"error": response.text}

        result = response.json()
        task_id = result["task_id"]

        if not wait_for_completion:
            return result

        # Poll for completion
        start_time = time.time()
        while True:
            if time.time() - start_time > timeout:
                return {"error": f"Timeout while waiting for task {task_id}"}

            status_response = requests.get(
                f"{self.base_url}/task/{task_id}", headers=self.headers
            )

            if not status_response.ok:
                return {"error": f"Failed to get task status: {status_response.text}"}

            status = status_response.json()

            if status["status"] == "completed":
                return status

            if status["status"] == "failed":
                return {"error": f"Task failed: {status.get('error', 'Unknown error')}"}

            # Wait before polling again
            time.sleep(2)

    def get_task_status(self, task_id: str) -> Dict:
        """Get the status of a task"""
        response = requests.get(f"{self.base_url}/task/{task_id}", headers=self.headers)

        if not response.ok:
            return {"error": f"Failed to get task status: {response.text}"}

        return response.json()
