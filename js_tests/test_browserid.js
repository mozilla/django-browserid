/* This Source Code Form is subject to the terms of the Mozilla Public
 * License, v. 2.0. If a copy of the MPL was not distributed with this
 * file, You can obtain one at http://mozilla.org/MPL/2.0/. */

// Fake server for XHRs.
var server;

function jsonResponse(obj) {
    return [200, {'Content-Type': 'application/json'}, JSON.stringify(obj)];
}

// Sets the response value for the info view.
function setInfoResponse(obj) {
    server.respondWith('GET', '/browserid/info/', jsonResponse(obj));
}

// Returns an already-resolved deferred with the given arguments.
// Useful for returning deferreds that just call their callbacks immediately.
function resolvedDeferred() {
    var deferred = $.Deferred();
    deferred.resolve.apply(deferred, arguments);
    return deferred;
}

suite('api.js', function() {
    setup(function() {
        server = sinon.fakeServer.create();
        navigator.id.reset();

        // Register handlers so mock Persona works.
        django_browserid._infoXHR = null;
        setInfoResponse({userEmail: 'test@example.com'});
        django_browserid.registerWatchHandlers();
        server.respond();

        // Reset info XHR and mock server so tests can use them.
        django_browserid._infoXHR = null;
        server.restore();
        server = sinon.fakeServer.create();
    });

    teardown(function() {
        server.restore();
    });

    test('login() should fetch an assertion and pass it to verifyAssertion.', function(done) {
        sinon.stub(django_browserid, 'getAssertion', function() {
            return resolvedDeferred('assertion');
        });
        sinon.stub(django_browserid, 'verifyAssertion', function() {
            return resolvedDeferred('verifyResult');
        });

        django_browserid.login({baz: 'biff'}).then(function(verifyResult) {
            sinon.assert.calledWith(django_browserid.getAssertion, {baz: 'biff'});
            sinon.assert.calledWith(django_browserid.verifyAssertion, 'assertion');
            chai.assert.equal(verifyResult, 'verifyResult');
            done();
        });

        server.respond();

        django_browserid.getAssertion.restore();
        django_browserid.verifyAssertion.restore();
    });

    test('logout() should call navigator.id.logout and send a POST to the ' +
         'logout view once Persona logs the user out.', function(done) {
        setInfoResponse({
            logoutUrl: '/browserid/logout/',
            csrfToken: 'csrfToken'
        });

        server.respondWith('POST', '/browserid/logout/', function(request) {
            chai.assert.equal(request.requestHeaders['X-CSRFToken'], 'csrfToken');
            request.respond.apply(request, jsonResponse({redirect: '/asdf/'}));
        });

        django_browserid.logout().then(function(logoutData) {
            chai.assert.ok(navigator.id.logout.called);
            chai.assert.deepEqual(logoutData, {redirect: '/asdf/'});
            done();
        });

        server.respond();
    });

    test('getAssertion() should call navigator.id.request and pass the given ' +
         'assertion to the Deferred once Persona finishes authing the user.', function(done) {
        setInfoResponse({
            requestArgs: {foo: 'bar'}
        });
        navigator.id.assertion = 'assertion';

        django_browserid.getAssertion({baz: 'biff'}).then(function(assertion) {
            chai.assert.equal(assertion, 'assertion');
            sinon.assert.calledWith(navigator.id.request, {foo: 'bar', baz: 'biff'});
            done();
        });

        server.respond();
    });

    test('verifyAssertion() should submit the given assertion to the login URL.', function(done) {
        setInfoResponse({
            loginUrl: '/browserid/login/',
            csrfToken: 'csrfToken'
        });

        server.respondWith('POST', '/browserid/login/', function(request) {
            chai.assert.equal(request.requestBody, 'assertion=assertion');
            chai.assert.equal(request.requestHeaders['X-CSRFToken'], 'csrfToken');
            request.respond.apply(request, jsonResponse({
                redirect: '/asdf/',
                email: 'a@test.com'
            }));
        });

        django_browserid.verifyAssertion('assertion').then(function(verifyResult) {
            chai.assert.deepEqual(verifyResult, {
                redirect: '/asdf/',
                email: 'a@test.com'
            });
            done();
        });

        server.respond();
    });

    test('getInfo() should return a jqXHR that returns the data from the info request.', function(done) {
        setInfoResponse({
            foo: 'bar'
        });

        django_browserid.getInfo().then(function(info) {
            chai.assert.deepEqual(info, {
                foo: 'bar'
            });
            done();
        });

        server.respond();
    });

    test('getInfo() should cache the response to the info request and only ' +
         'send the request once.', function(done) {
        setInfoResponse({
            foo: 'bar'
        });

        django_browserid.getInfo().then(function(info) {
            django_browserid.getInfo().then(function(info2) {
                chai.assert.lengthOf(server.requests, 1);
                done();
            });
        });

        server.respond();
    });

    test('didLoginFail() should return true of `bid_login_failed=1` is in the querystring.', function() {
        var location = {search: 'foo=bar'};
        chai.assert.notOk(django_browserid.didLoginFail(location));

        location = {search: 'foo=bar&bid_login_failed=1&baz=biff'};
        chai.assert.ok(django_browserid.didLoginFail(location));
    });

    test('registerWatchHandlers() should pass the userEmail from the info ' +
         'response to navigator.id.watch.', function(done) {
        setInfoResponse({
            userEmail: 'test@example.com'
        });
        navigator.id.reset(); // Clear out the handlers registered in setup.

        django_browserid.registerWatchHandlers().then(function() {
            var watch_arg = navigator.id.watch.args[0][0];
            chai.assert.equal(watch_arg.loggedInUser, 'test@example.com');
            done();
        });

        server.respond();
    });

    test('If login failed, registerWatchHandlers() shouldlog the user out the ' +
         'first time onlogin is called.', function(done) {
        setInfoResponse({
            userEmail: 'test@example.com'
        });
        navigator.id.reset(); // Clear out the handlers registered in setup.
        sinon.stub(django_browserid, 'didLoginFail').returns(true);

        django_browserid.registerWatchHandlers().then(function() {
            var watch_arg = navigator.id.watch.args[0][0];
            watch_arg.onlogin('assertion');
            chai.assert.ok(navigator.id.logout.called);
            done();
        });

        server.respond();
        django_browserid.didLoginFail.restore();
    });
});
