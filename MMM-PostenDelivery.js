Module.register("MMM-PostenDelivery", {
    defaults: {
        postalCode: ""
    },

    start: function() {
        this.deliveryInfo = null;
        this.sendSocketNotification("GET_POSTEN_DELIVERY_DAYS", this.config.postalCode);
    },

    socketNotificationReceived: function(notification, payload) {
        if (notification === "POSTEN_DELIVERY_DAYS") {
            this.deliveryInfo = payload;
            this.updateDom();
        }
        if (notification === "POSTEN_DELIVERY_DAYS_ERROR") {
            console.error("Error receiving delivery days:", payload.error);
        }
    },

    getDom: function() {
        var wrapper = document.createElement("div");
        if (!this.deliveryInfo) {
            wrapper.innerHTML = "Laster postleveringsdager...";
        } else if (this.deliveryInfo.error) {
            wrapper.innerHTML = `Error: ${this.deliveryInfo.error}`;
        } else {
            wrapper.innerHTML = `Neste postlevering er ${this.deliveryInfo.next_delivery}.`;
        }
        return wrapper;
    }
});
