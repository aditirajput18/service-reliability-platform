const form = document.getElementById("service-form");
const container = document.getElementById("services-container");
const message = document.getElementById("message");
const refreshButton = document.getElementById("refresh-button");


async function loadServices() {
    try {
        const response = await fetch("/api/services");

        if (!response.ok) {
            throw new Error("Failed to load services");
        }

        const services = await response.json();

        if (services.length === 0) {
            container.innerHTML =
                "<p>No services registered yet.</p>";
            return;
        }

        container.innerHTML = "";

        for (const service of services) {
            const element = document.createElement("div");

            element.className = "service";

            const status = service.last_status || "NOT CHECKED";

            const statusClass =
                service.last_status === "UP"
                    ? "status-up"
                    : service.last_status === "DOWN"
                        ? "status-down"
                        : "status-unknown";

            const httpStatus =
                service.last_http_status !== null
                    ? service.last_http_status
                    : "—";

            const responseTime =
                service.last_response_time_ms !== null
                    ? `${service.last_response_time_ms} ms`
                    : "—";

            const lastChecked =
                service.last_checked_at
                    ? new Date(
                        service.last_checked_at
                    ).toLocaleString()
                    : "Never";

            let metrics = null;
            let alerts = [];
	    let incidents = [];
            try {
                const metricsResponse = await fetch(
                    `/api/services/${service.id}/metrics`
                );

                if (metricsResponse.ok) {
                    metrics = await metricsResponse.json();
                }
            } catch (error) {
                console.error(
                    `Failed to load metrics for service ${service.id}`,
                    error
                );
            }

            try {
                const incidentsResponse = await fetch(
                    `/api/services/${service.id}/incidents`
                );

                if (incidentsResponse.ok) {
                    incidents = await incidentsResponse.json();
                }
            } catch (error) {
                console.error(
                    `Failed to load incidents for service ${service.id}`,
                    error
                );
            }

            try {
                const alertsResponse = await fetch(
                    `/api/services/${service.id}/alerts`
                );

                if (alertsResponse.ok) {
                    alerts = await alertsResponse.json();
                }
            } catch (error) {
                console.error(
                    `Failed to load alerts for service ${service.id}`,
                    error
                );
            }

            const activeAlerts = alerts.filter(
                alert => alert.status === "ACTIVE"
            );

	    const activeIncidents = incidents.filter(
    		incident => incident.status !== "RESOLVED"
	    );

            let alertsHtml = "";

            if (activeAlerts.length > 0) {
                alertsHtml = `
                    <div class="alerts-info alert-active">
                        <h4>🚨 Active Alerts</h4>

                        ${activeAlerts.map(alert => `
                            <div class="alert-item">
                                <p>
                                    <strong>${escapeHtml(alert.alert_type)}</strong>
                                </p>

                                <p>
                                    ${escapeHtml(alert.message)}
                                </p>

                                <p>
                                    <strong>Created:</strong>
                                    ${new Date(
                                        alert.created_at
                                    ).toLocaleString()}
                                </p>
                            </div>
                        `).join("")}
                    </div>
                `;
            } else {
                alertsHtml = `
                    <div class="alerts-info alert-healthy">
                        <h4>✅ Alerts</h4>
                        <p>No active alerts.</p>
                    </div>
                `;
            }

            let incidentsHtml = "";

            if (activeIncidents.length > 0) {
                incidentsHtml = `
                    <div class="incidents-info incident-active">
                        <h4>📋 Active Incidents</h4>

                        ${activeIncidents.map(incident => `
                            <div class="incident-item">

                                <p>
                                    <strong>
                                        ${escapeHtml(incident.title)}
                                    </strong>
                                </p>

                                <p>
                                    ${escapeHtml(
                                        incident.description
                                    )}
                                </p>

                                <p>
                                    <strong>Status:</strong>
                                    ${escapeHtml(incident.status)}
                                </p>

                                <p>
                                    <strong>Created:</strong>
                                    ${new Date(
                                        incident.created_at
                                    ).toLocaleString()}
                                </p>

                            </div>
                        `).join("")}
                    </div>
                `;
            } else {
                incidentsHtml = `
                    <div class="incidents-info incident-healthy">
                        <h4>📋 Incidents</h4>
                        <p>No active incidents.</p>
                    </div>
                `;
            }

            let incidentHistoryHtml = "";

            if (incidents.length > 0) {
                incidentHistoryHtml = `
                    <div class="incident-history">
                        <h4>Incident History</h4>

                        ${incidents.map(incident => `
                            <div class="incident-history-item">

                                <p>
                                    <strong>
                                        #${incident.id}
                                    </strong>

                                    ${escapeHtml(
                                        incident.title
                                    )}
                                </p>

                                <p>
                                    <strong>Status:</strong>
                                    ${escapeHtml(
                                        incident.status
                                    )}
                                </p>

                            </div>
                        `).join("")}
                    </div>
                `;
            }

            element.innerHTML = `
                <h3>
                    ${escapeHtml(service.name)}
                </h3>

                <p>
                    <strong>URL:</strong>
                    ${escapeHtml(service.url)}
                </p>

                <p>
                    ${escapeHtml(
                        service.description ||
                        "No description"
                    )}
                </p>

                <div class="health-info">

                    <p>
                        <strong>Status:</strong>
                        <span class="${statusClass}">
                            ${status}
                        </span>
                    </p>

                    <p>
                        <strong>HTTP:</strong>
                        ${httpStatus}
                    </p>

                    <p>
                        <strong>Response:</strong>
                        ${responseTime}
                    </p>

                    <p>
                        <strong>Last checked:</strong>
                        ${lastChecked}
                    </p>

                </div>

                <div class="metrics-info">

                    <h4>Monitoring Metrics</h4>

                    <p>
                        <strong>Total Checks:</strong>
                        ${metrics ? metrics.total_checks : "—"}
                    </p>

                    <p>
                        <strong>Successful:</strong>
                        ${metrics ? metrics.successful_checks : "—"}
                    </p>

                    <p>
                        <strong>Failed:</strong>
                        ${metrics ? metrics.failed_checks : "—"}
                    </p>

                    <p>
                        <strong>Uptime:</strong>
                        ${metrics
                            ? `${metrics.uptime_percentage}%`
                            : "—"}
                    </p>

                    <p>
                        <strong>Avg Response:</strong>
                        ${metrics
                            ? `${metrics.average_response_time_ms} ms`
                            : "—"}
                    </p>

                </div>

                ${alertsHtml}
		${incidentsHtml}
		${incidentHistoryHtml}

                <button
                    class="check-button"
                    onclick="checkService(${service.id}, this)"
                >
                    Check Now
                </button>

                <button
                    class="delete-button"
                    onclick="deleteService(${service.id})"
                >
                    Delete
                </button>
            `;

            container.appendChild(element);
        }

    } catch (error) {
        container.innerHTML =
            "<p>Unable to load services.</p>";

        console.error(error);
    }
}


async function checkService(id, button) {
    const originalText = button.textContent;

    button.disabled = true;
    button.textContent = "Checking...";

    try {
        const response = await fetch(
            `/api/services/${id}/check`,
            {
                method: "POST"
            }
        );

        const data = await response.json();

        if (!response.ok) {
            throw new Error(
                data.detail || "Health check failed"
            );
        }

        await loadServices();

    } catch (error) {
        alert(error.message);

        button.disabled = false;
        button.textContent = originalText;
    }
}


form.addEventListener("submit", async event => {
    event.preventDefault();

    const service = {
        name: document.getElementById("name").value,
        url: document.getElementById("url").value,
        description:
            document.getElementById("description").value
    };

    try {
        const response = await fetch(
            "/api/services",
            {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify(service)
            }
        );

        const data = await response.json();

        if (!response.ok) {
            throw new Error(
                data.detail ||
                "Failed to create service"
            );
        }

        message.textContent =
            "Service registered successfully.";

        form.reset();

        await loadServices();

    } catch (error) {
        message.textContent = error.message;
    }
});


async function deleteService(id) {
    try {
        const response = await fetch(
            `/api/services/${id}`,
            {
                method: "DELETE"
            }
        );

        if (!response.ok) {
            throw new Error(
                "Failed to delete service"
            );
        }

        await loadServices();

    } catch (error) {
        alert(error.message);
    }
}


function escapeHtml(value) {
    const div = document.createElement("div");

    div.textContent = value;

    return div.innerHTML;
}


refreshButton.addEventListener(
    "click",
    loadServices
);


loadServices();
