"""
Example: Webview with data visualization - Real-time charts
"""

import random
import threading
import time

from vscode_sockpuppet import VSCodeClient, WebviewOptions


class ChartState:
    """Manages chart data state."""

    def __init__(self):
        self.data_points = []
        self.max_points = 20
        self.paused = False
        self.disposed = threading.Event()

    def add_data_point(self, value):
        """Add a data point to the chart."""
        timestamp = time.strftime("%H:%M:%S")
        self.data_points.append({"time": timestamp, "value": value})

        # Keep only the last max_points
        if len(self.data_points) > self.max_points:
            self.data_points.pop(0)

    def pause(self):
        """Pause the data stream."""
        self.paused = True

    def resume(self):
        """Resume the data stream."""
        self.paused = False

    def clear(self):
        """Clear all data points."""
        self.data_points.clear()

    def stop(self):
        """Signal that the webview was disposed."""
        self.disposed.set()


with VSCodeClient() as client:
    print("Creating real-time data visualization...")

    html_content = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <meta http-equiv="Content-Security-Policy" content="default-src 'none'; script-src https://cdn.jsdelivr.net 'unsafe-inline'; style-src 'unsafe-inline'; img-src data:;">
        <title>Data Visualization</title>
        <script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>
        <style>
            body {
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                padding: 20px;
                background-color: var(--vscode-editor-background);
                color: var(--vscode-editor-foreground);
            }
            .container {
                max-width: 900px;
                margin: 0 auto;
            }
            h1 {
                color: var(--vscode-textLink-foreground);
            }
            .chart-container {
                position: relative;
                height: 400px;
                margin: 20px 0;
                background-color: var(--vscode-editor-background);
                padding: 20px;
                border-radius: 5px;
                border: 1px solid var(--vscode-input-border);
            }
            .stats {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
                gap: 15px;
                margin-top: 20px;
            }
            .stat-card {
                padding: 15px;
                background-color: var(--vscode-editor-selectionBackground);
                border-radius: 3px;
                border-left: 4px solid var(--vscode-textLink-foreground);
            }
            .stat-label {
                font-size: 12px;
                opacity: 0.8;
            }
            .stat-value {
                font-size: 24px;
                font-weight: bold;
                margin-top: 5px;
            }
            .controls {
                margin-top: 20px;
                text-align: center;
            }
            button {
                background-color: var(--vscode-button-background);
                color: var(--vscode-button-foreground);
                border: none;
                padding: 10px 20px;
                cursor: pointer;
                border-radius: 3px;
                font-size: 14px;
                margin: 5px;
            }
            button:hover {
                background-color: var(--vscode-button-hoverBackground);
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>📊 Real-Time Data Visualization</h1>
            <p>Python is generating random data and updating this chart in real-time.</p>

            <div class="chart-container">
                <canvas id="myChart"></canvas>
            </div>

            <div class="stats">
                <div class="stat-card">
                    <div class="stat-label">Current Value</div>
                    <div class="stat-value" id="currentValue">-</div>
                </div>
                <div class="stat-card">
                    <div class="stat-label">Average</div>
                    <div class="stat-value" id="avgValue">-</div>
                </div>
                <div class="stat-card">
                    <div class="stat-label">Maximum</div>
                    <div class="stat-value" id="maxValue">-</div>
                </div>
                <div class="stat-card">
                    <div class="stat-label">Minimum</div>
                    <div class="stat-value" id="minValue">-</div>
                </div>
            </div>

            <div class="controls">
                <button onclick="sendMessage('pause')">⏸️ Pause</button>
                <button onclick="sendMessage('resume')">▶️ Resume</button>
                <button onclick="sendMessage('clear')">🗑️ Clear Data</button>
            </div>
        </div>

        <script>
            const vscode = acquireVsCodeApi();

            // Initialize Chart.js
            const ctx = document.getElementById('myChart').getContext('2d');
            const chart = new Chart(ctx, {
                type: 'line',
                data: {
                    labels: [],
                    datasets: [{
                        label: 'Data Stream',
                        data: [],
                        borderColor: 'rgb(75, 192, 192)',
                        backgroundColor: 'rgba(75, 192, 192, 0.1)',
                        tension: 0.4,
                        fill: true
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: {
                            labels: {
                                color: getComputedStyle(document.body).color
                            }
                        }
                    },
                    scales: {
                        y: {
                            beginAtZero: true,
                            grid: {
                                color: 'rgba(255, 255, 255, 0.1)'
                            },
                            ticks: {
                                color: getComputedStyle(document.body).color
                            }
                        },
                        x: {
                            grid: {
                                color: 'rgba(255, 255, 255, 0.1)'
                            },
                            ticks: {
                                color: getComputedStyle(document.body).color
                            }
                        }
                    }
                }
            });

            function sendMessage(action) {
                vscode.postMessage({ action: action });
            }

            // Listen for data updates from Python
            window.addEventListener('message', event => {
                const message = event.data;

                if (message.type === 'updateData') {
                    const dataPoints = message.data;

                    // Update chart
                    chart.data.labels = dataPoints.map(d => d.time);
                    chart.data.datasets[0].data = dataPoints.map(d => d.value);
                    chart.update('none'); // No animation for smooth updates

                    // Update stats
                    if (dataPoints.length > 0) {
                        const values = dataPoints.map(d => d.value);
                        const current = values[values.length - 1];
                        const avg = values.reduce((a, b) => a + b, 0) / values.length;
                        const max = Math.max(...values);
                        const min = Math.min(...values);

                        document.getElementById('currentValue').textContent = current.toFixed(1);
                        document.getElementById('avgValue').textContent = avg.toFixed(1);
                        document.getElementById('maxValue').textContent = max.toFixed(1);
                        document.getElementById('minValue').textContent = min.toFixed(1);
                    }
                }
            });
        </script>
    </body>
    </html>
    """

    options = WebviewOptions(enable_scripts=True, retain_context_when_hidden=True)

    with client.window.create_webview_panel(
        title="Data Visualization", html=html_content, options=options
    ) as panel:
        print(f"Created webview panel: {panel.id}")

        state = ChartState()

        # Handle disposal
        def on_dispose():
            print("\n✓ Webview closed")
            state.stop()

        panel.on_did_dispose(on_dispose)

        # Handle messages from webview
        def handle_message(message):
            action = message.get("action")

            if action == "pause":
                state.pause()
                print("⏸️  Data stream paused")
                client.window.show_information_message("Data stream paused")

            elif action == "resume":
                state.resume()
                print("▶️  Data stream resumed")
                client.window.show_information_message("Data stream resumed")

            elif action == "clear":
                state.clear()
                panel.post_message({"type": "updateData", "data": []})
                print("🗑️  Data cleared")
                client.window.show_information_message("Data cleared")

        panel.on_did_receive_message(handle_message)

        print("\n📊 Real-time visualization started!")
        print("Generating random data every second...")
        print("Use the buttons to pause/resume or clear the chart.")
        print("Close the webview to exit.\n")

        # Generate and send data periodically
        while not state.disposed.is_set():
            if not state.paused:
                # Generate random data point
                value = 50 + random.uniform(-20, 20)
                state.add_data_point(value)

                # Send updated data to webview
                panel.post_message({"type": "updateData", "data": state.data_points})

                print(f"📈 Sent data point: {value:.1f}")

            # Wait for 1 second or until disposed
            if state.disposed.wait(timeout=1.0):
                break

        print("\n✅ Visualization demo complete!")
