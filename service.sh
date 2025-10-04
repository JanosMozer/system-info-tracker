#!/bin/bash
# System Info Tracker service management script

case "$1" in
    start)
        echo "Starting System Info Tracker service..."
        sudo systemctl start system-info-tracker.service
        ;;
    stop)
        echo "Stopping System Info Tracker service..."
        sudo systemctl stop system-info-tracker.service
        ;;
    restart)
        echo "Restarting System Info Tracker service..."
        sudo systemctl restart system-info-tracker.service
        ;;
    status)
        echo "System Info Tracker service status:"
        sudo systemctl status system-info-tracker.service
        ;;
    logs)
        echo "System Info Tracker service logs:"
        sudo journalctl -u system-info-tracker.service -f --no-pager
        ;;
    enable)
        echo "Enabling System Info Tracker service to start on boot..."
        sudo systemctl enable system-info-tracker.service
        ;;
    disable)
        echo "Disabling System Info Tracker service from starting on boot..."
        sudo systemctl disable system-info-tracker.service
        ;;
    *)
        echo "Usage: $0 {start|stop|restart|status|logs|enable|disable}"
        echo ""
        echo "Commands:"
        echo "  start   - Start the service"
        echo "  stop    - Stop the service" 
        echo "  restart - Restart the service"
        echo "  status  - Show service status"
        echo "  logs    - Show live service logs"
        echo "  enable  - Enable auto-start on boot"
        echo "  disable - Disable auto-start on boot"
        exit 1
        ;;
esac

exit 0