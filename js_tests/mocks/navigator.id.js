function MockNavigatorId() {
    var self = this;
    self.watch_data = null;
    self.assertion = 'assertion';

    self.watch = sinon.spy(function(data) {
        self.watch_data = data;
    });

    self.request = sinon.spy(function() {
        self.watch_data.onlogin(self.assertion);
    });

    self.logout = sinon.spy(function() {
        self.watch_data.onlogout();
    });
}

MockNavigatorId.prototype = {
    reset: function() {
        this.watch.reset();
        this.request.reset();
        this.logout.reset();
        this.watch_data = null;
    }
};

window.navigator.id = new MockNavigatorId();
