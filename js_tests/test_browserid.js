/* This Source Code Form is subject to the terms of the Mozilla Public
 * License, v. 2.0. If a copy of the MPL was not distributed with this
 * file, You can obtain one at http://mozilla.org/MPL/2.0/. */

// Fake server for XHRs.
var server;

function jsonResponse(obj) {
    return [200, {'Content-Type': 'application/json'}, JSON.stringify(obj)];
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
        django_browserid.registerWatchHandlers();

        // Reset requestDeferred in case someone set it.
        django_browserid._requestDeferred = null;

        // Mock our CSRF view to return 'csrfToken'.
        server.respondWith('GET', '/browserid/csrf/', [200, {}, 'csrfToken']);
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

        django_browserid.login({baz: 'biff'}, 'nextUrl').then(function(verifyResult) {
            sinon.assert.calledWith(django_browserid.getAssertion, {baz: 'biff'});
            sinon.assert.calledWith(django_browserid.verifyAssertion, 'assertion', 'nextUrl');
            chai.assert.equal(verifyResult, 'verifyResult');
            done();
        });

        server.respond();

        django_browserid.getAssertion.restore();
        django_browserid.verifyAssertion.restore();
    });

    test('If the first argument to login() is a string, treat it as the next parameter.', function(done) {
        sinon.stub(django_browserid, 'getAssertion', function() {
            return resolvedDeferred('assertion');
        });
        sinon.stub(django_browserid, 'verifyAssertion', function() {
            return resolvedDeferred('verifyResult');
        });

        django_browserid.login('nextUrl').then(function(verifyResult) {
            sinon.assert.calledWith(django_browserid.getAssertion, undefined);
            sinon.assert.calledWith(django_browserid.verifyAssertion, 'assertion', 'nextUrl');
            chai.assert.equal(verifyResult, 'verifyResult');
            done();
        });

        server.respond();

        django_browserid.getAssertion.restore();
        django_browserid.verifyAssertion.restore();
    });

    test('logout() should send a POST to the logout view to log the user out.', function(done) {
        sinon.stub(django_browserid, 'getInfo', function() {
            return {csrfUrl: '/browserid/csrf/', logoutUrl: '/browserid/logout/'};
        });

        server.respondWith('POST', '/browserid/logout/', function(request) {
            chai.assert.equal(request.requestHeaders['X-CSRFToken'], 'csrfToken');
            chai.assert.equal(request.requestBody, 'next=nextUrl');
            request.respond.apply(request, jsonResponse({redirect: '/asdf/'}));
        });

        django_browserid.logout('nextUrl').then(function(logoutData) {
            chai.assert.deepEqual(logoutData, {redirect: '/asdf/'});
            done();
        });

        server.respond();
        django_browserid.getInfo.restore();
    });

    test('getAssertion() should call navigator.id.request and pass the given ' +
         'assertion to the Deferred once Persona finishes authing the user.', function(done) {
        sinon.stub(django_browserid, 'getInfo', function() {
            return {requestArgs: {foo: 'bar'}};
        });
        navigator.id.assertion = 'assertion';

        django_browserid.getAssertion({baz: 'biff'}).then(function(assertion) {
            chai.assert.equal(assertion, 'assertion');
            sinon.assert.calledWith(navigator.id.request, {foo: 'bar', baz: 'biff'});
            done();
        });

        server.respond();
        django_browserid.getInfo.restore();
    });

    test('verifyAssertion() should submit the given assertion to the login URL.', function(done) {
        sinon.stub(django_browserid, 'getInfo', function() {
            return {csrfUrl: '/browserid/csrf/', loginUrl: '/browserid/login/'};
        });

        server.respondWith('POST', '/browserid/login/', function(request) {
            chai.assert.equal(request.requestBody, 'assertion=assertion&next=nextUrl');
            chai.assert.equal(request.requestHeaders['X-CSRFToken'], 'csrfToken');
            request.respond.apply(request, jsonResponse({
                redirect: '/asdf/',
                email: 'a@test.com'
            }));
        });

        django_browserid.verifyAssertion('assertion', 'nextUrl').then(function(verifyResult) {
            chai.assert.deepEqual(verifyResult, {
                redirect: '/asdf/',
                email: 'a@test.com'
            });
            done();
        });

        server.respond();
        django_browserid.getInfo.restore();
    });

    test('getCsrfToken() should return a jqXHR that returns the csrf token.', function(done) {
        sinon.stub(django_browserid, 'getInfo', function() {
            return {csrfUrl: '/browserid/csrf/'};
        });

        django_browserid.getCsrfToken().then(function(token) {
            chai.assert.equal(token, 'csrfToken');
            done();
        });

        server.respond();
        django_browserid.getInfo.restore();
    });

    test('registerWatchHandlers() should call onAutoLogin if onLogin is called ' +
         'when getAssertion wasn\'t called.', function() {
        navigator.id.reset();
        var onAutoLogin = sinon.spy();
        django_browserid.registerWatchHandlers(onAutoLogin);

        // Simulate automatically-triggered login by accessing watch data
        // directly.
        navigator.id.watch_data.onlogin('assertion');
        chai.assert.ok(onAutoLogin.calledWith('assertion'));
    });
});
