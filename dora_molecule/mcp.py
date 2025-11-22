"""DORA Metrics MCP Molecule with self-hosted JS component rendering.

This demo showcases how a devgraph MCP server can host both:
1. MCP tools for data retrieval
2. Static JS components for visualization (RemotePlugin pattern)
"""

import random
from datetime import datetime, timedelta
from pathlib import Path
from typing import Literal

from loguru import logger
from pydantic import BaseModel

from devgraph_integrations.mcpserver.plugin import DevgraphMCPPlugin


class DoraConfig(BaseModel):
    """Configuration for DORA MCP Molecule.

    Attributes:
        base_url: Base URL where this server is accessible (for component URLs)
    """

    base_url: str = "http://localhost:9000"


class DoraMCPMolecule(DevgraphMCPPlugin):
    """MCP molecule providing DORA metrics tools with self-hosted JS components.

    This demonstrates the RemotePlugin pattern where the MCP server serves
    both the tool implementations and the JS components that render the results.

    DORA Metrics:
    - Deployment Frequency: How often code is deployed to production
    - Lead Time for Changes: Time from commit to production
    - Mean Time to Recovery (MTTR): Time to restore service after incident
    - Change Failure Rate: Percentage of deployments causing failures
    """

    config_type = DoraConfig
    plugin_fqdn = "dora.molecules.devgraph.ai"

    # Static assets this molecule provides - the server will serve these
    # Path will be: /static/dora.molecules.devgraph.ai/1.0.0/dora-metrics.js
    static_assets = {
        "dora-metrics.js": Path(__file__).parent.parent / "static" / "dora-metrics.js",
    }
    static_assets_version = "1.0.0"

    def __init__(self, app, config: DoraConfig):
        super().__init__(app, config)

        # Register MCP tools
        self.app.add_tool(self.get_dora_metrics)
        self.app.add_tool(self.get_deployment_frequency)
        self.app.add_tool(self.get_lead_time)
        self.app.add_tool(self.get_mttr)
        self.app.add_tool(self.get_change_failure_rate)
        self.app.add_tool(self.list_deployments)

        logger.info("DORA Molecule initialized")

    def _generate_sample_metrics(self, service: str, days: int = 30) -> dict:
        """Generate sample DORA metrics data for demo purposes."""
        # Simulate metrics that vary by service
        service_hash = hash(service) % 100

        return {
            "service": service,
            "period_days": days,
            "deployment_frequency": {
                "value": round(random.uniform(1, 10) + (service_hash / 50), 2),
                "unit": "deployments_per_day",
                "rating": "elite" if service_hash > 70 else "high" if service_hash > 40 else "medium",
            },
            "lead_time_for_changes": {
                "value": round(random.uniform(0.5, 24) + (100 - service_hash) / 10, 2),
                "unit": "hours",
                "rating": "elite" if service_hash > 60 else "high" if service_hash > 30 else "medium",
            },
            "mean_time_to_recovery": {
                "value": round(random.uniform(0.1, 4) + (100 - service_hash) / 25, 2),
                "unit": "hours",
                "rating": "elite" if service_hash > 50 else "high" if service_hash > 20 else "medium",
            },
            "change_failure_rate": {
                "value": round(random.uniform(0, 15) + (100 - service_hash) / 10, 2),
                "unit": "percent",
                "rating": "elite" if service_hash > 65 else "high" if service_hash > 35 else "medium",
            },
        }

    def get_dora_metrics(
        self,
        service: str,
        days: int = 30,
    ) -> dict:
        """Get all four DORA metrics for a service.

        Args:
            service: Service/application name to get metrics for
            days: Number of days to calculate metrics over (default 30)

        Returns:
            Dictionary containing all DORA metrics with ratings and a JS component
            for visualization
        """
        logger.info(f"Getting DORA metrics for {service} over {days} days")

        metrics = self._generate_sample_metrics(service, days)

        # Return with renderer metadata for RemotePlugin
        return {
            **metrics,
            "_meta": {
                "renderer": {
                    "type": "remote",
                    "source": self.static_url("dora-metrics.js"),
                }
            },
        }

    def get_deployment_frequency(
        self,
        service: str,
        days: int = 30,
    ) -> dict:
        """Get deployment frequency metric for a service.

        Deployment Frequency measures how often an organization successfully
        releases to production.

        Elite performers: Multiple deploys per day
        High performers: Between once per day and once per week
        Medium performers: Between once per week and once per month
        Low performers: Less than once per month

        Args:
            service: Service/application name
            days: Number of days to analyze

        Returns:
            Deployment frequency data with rating
        """
        logger.info(f"Getting deployment frequency for {service}")

        # Generate sample deployments
        num_deployments = random.randint(days // 2, days * 3)
        deployments_per_day = round(num_deployments / days, 2)

        if deployments_per_day >= 1:
            rating = "elite"
        elif deployments_per_day >= 0.14:  # ~weekly
            rating = "high"
        elif deployments_per_day >= 0.03:  # ~monthly
            rating = "medium"
        else:
            rating = "low"

        return {
            "service": service,
            "metric": "deployment_frequency",
            "total_deployments": num_deployments,
            "period_days": days,
            "value": deployments_per_day,
            "unit": "deployments_per_day",
            "rating": rating,
        }

    def get_lead_time(
        self,
        service: str,
        days: int = 30,
    ) -> dict:
        """Get lead time for changes metric for a service.

        Lead Time for Changes measures the amount of time it takes for a commit
        to get into production.

        Elite performers: Less than one hour
        High performers: Between one day and one week
        Medium performers: Between one week and one month
        Low performers: More than one month

        Args:
            service: Service/application name
            days: Number of days to analyze

        Returns:
            Lead time data with rating
        """
        logger.info(f"Getting lead time for {service}")

        # Generate sample lead time in hours
        lead_time_hours = round(random.uniform(0.5, 72), 2)

        if lead_time_hours < 1:
            rating = "elite"
        elif lead_time_hours < 24:
            rating = "high"
        elif lead_time_hours < 168:  # 1 week
            rating = "medium"
        else:
            rating = "low"

        return {
            "service": service,
            "metric": "lead_time_for_changes",
            "value": lead_time_hours,
            "unit": "hours",
            "rating": rating,
            "period_days": days,
        }

    def get_mttr(
        self,
        service: str,
        days: int = 30,
    ) -> dict:
        """Get Mean Time to Recovery metric for a service.

        MTTR measures how long it takes to restore service when an incident
        or defect that impacts users occurs.

        Elite performers: Less than one hour
        High performers: Less than one day
        Medium performers: Between one day and one week
        Low performers: More than one week

        Args:
            service: Service/application name
            days: Number of days to analyze

        Returns:
            MTTR data with rating
        """
        logger.info(f"Getting MTTR for {service}")

        # Generate sample incidents
        num_incidents = random.randint(1, 10)
        avg_recovery_hours = round(random.uniform(0.1, 48), 2)

        if avg_recovery_hours < 1:
            rating = "elite"
        elif avg_recovery_hours < 24:
            rating = "high"
        elif avg_recovery_hours < 168:
            rating = "medium"
        else:
            rating = "low"

        return {
            "service": service,
            "metric": "mean_time_to_recovery",
            "incidents_count": num_incidents,
            "value": avg_recovery_hours,
            "unit": "hours",
            "rating": rating,
            "period_days": days,
        }

    def get_change_failure_rate(
        self,
        service: str,
        days: int = 30,
    ) -> dict:
        """Get Change Failure Rate metric for a service.

        Change Failure Rate measures the percentage of deployments causing a
        failure in production.

        Elite performers: 0-15%
        High performers: 16-30%
        Medium performers: 31-45%
        Low performers: 46-100%

        Args:
            service: Service/application name
            days: Number of days to analyze

        Returns:
            Change failure rate data with rating
        """
        logger.info(f"Getting change failure rate for {service}")

        # Generate sample data
        total_deployments = random.randint(10, 100)
        failed_deployments = random.randint(0, total_deployments // 3)
        failure_rate = round((failed_deployments / total_deployments) * 100, 2)

        if failure_rate <= 15:
            rating = "elite"
        elif failure_rate <= 30:
            rating = "high"
        elif failure_rate <= 45:
            rating = "medium"
        else:
            rating = "low"

        return {
            "service": service,
            "metric": "change_failure_rate",
            "total_deployments": total_deployments,
            "failed_deployments": failed_deployments,
            "value": failure_rate,
            "unit": "percent",
            "rating": rating,
            "period_days": days,
        }

    def list_deployments(
        self,
        service: str,
        limit: int = 10,
        status: Literal["all", "success", "failed"] = "all",
    ) -> dict:
        """List recent deployments for a service.

        Args:
            service: Service/application name
            limit: Maximum number of deployments to return
            status: Filter by deployment status

        Returns:
            List of deployments with metadata
        """
        logger.info(f"Listing deployments for {service} (limit={limit}, status={status})")

        # Generate sample deployments
        deployments = []
        now = datetime.now()

        for i in range(limit):
            deploy_time = now - timedelta(hours=random.randint(1, 720))
            deploy_status = random.choice(["success", "success", "success", "failed"])

            if status != "all" and deploy_status != status:
                continue

            deployments.append({
                "id": f"deploy-{hash(f'{service}-{i}') % 10000:04d}",
                "service": service,
                "version": f"v1.{random.randint(0, 50)}.{random.randint(0, 100)}",
                "status": deploy_status,
                "timestamp": deploy_time.isoformat(),
                "duration_seconds": random.randint(30, 600),
                "author": random.choice(["alice", "bob", "charlie", "diana"]),
                "commit_sha": f"{random.randint(0, 0xFFFFFF):06x}",
            })

        # Sort by timestamp descending
        deployments.sort(key=lambda d: d["timestamp"], reverse=True)

        return {
            "service": service,
            "deployments": deployments[:limit],
            "total": len(deployments),
        }
