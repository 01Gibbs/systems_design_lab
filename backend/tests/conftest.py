import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../src')))

# Disable OpenTelemetry during tests to prevent hanging on shutdown
os.environ["OTEL_SDK_DISABLED"] = "true"
