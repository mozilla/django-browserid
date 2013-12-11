/* This Source Code Form is subject to the terms of the Mozilla Public
 * License, v. 2.0. If a copy of the MPL was not distributed with this
 * file, You can obtain one at http://mozilla.org/MPL/2.0/. */

;(function($, navigator, window_location) {
    'use strict';

    // Deferred for post-watch-callback actions.
    var requestDeferred = null;
    var logoutDeferred = null;

    // Track if we've avoided the first auto-login.
    var avoidedAutoLogin = false;

    // Public API
    var django_browserid = {
        /**
         * Retrieve an assertion and use it to log the user into your site.
         * @param {object} requestArgs Options to pass to navigator.id.request.
         * @return {jQuery.Deferred} Deferred that resolves once the user has
         *                           been logged in.
         */
        login: function login(requestArgs) {
            return django_browserid.getAssertion(requestArgs).then(function(assertion) {
                return django_browserid.verifyAssertion(assertion);
            });
        },

        /**
         * Log the user out of your site.
         * @return {jQuery.Deferred} Deferred that resolves once the user has
         *                           been logged out.
         */
        logout: function logout() {
            return django_browserid.getInfo().then(function(info) {
                logoutDeferred = $.Deferred();
                navigator.id.logout();

                return logoutDeferred.then(function() {
                    return $.ajax(info.logoutUrl, {
                        type: 'POST',
                        headers: {'X-CSRFToken': info.csrfToken},
                    });
                });
            });
        },

        /**
         * Retrieve an assertion via BrowserID.
         * @param {object} requestArgs Options to pass to navigator.id.request.
         * @return {jQuery.Deferred} Deferred that resolves with the assertion
         *                           once it is retrieved.
         */
        getAssertion: function getAssertion(requestArgs) {
            return django_browserid.getInfo().then(function(info) {
                requestArgs = $.extend({}, info.requestArgs, requestArgs);

                requestDeferred = $.Deferred();
                navigator.id.request(requestArgs);
                return requestDeferred;
            });
        },

        /**
         * Verify that the given assertion is valid, and log the user in.
         * @param {string} Assertion to verify.
         * @return {jQuery.Deferred} Deferred that resolves with the login view
         *                           response once login is complete.
         */
        verifyAssertion: function verifyAssertion(assertion) {
            return django_browserid.getInfo().then(function(info) {
                return $.ajax(info.loginUrl, {
                    type: 'POST',
                    data: {assertion: assertion},
                    headers: {'X-CSRFToken': info.csrfToken},
                });
            });
        },

        // Cache for the AJAX request created by django_browserid.getInfo().
        // Stored on the public API so tests can reset it.
        _infoXHR: null,

        /**
         * Fetch the info for the Persona popup and login requests.
         * @return {jqXHR} jQuery XmlHttpResponse that returns the data.
         */
        getInfo: function getInfo() {
            if (django_browserid._infoXHR === null) {
                django_browserid._infoXHR = $.get('/browserid/info/');
            }

            return django_browserid._infoXHR;
        },

        /**
         * Check for the querystring parameter used to signal a failed login.
         * @param {Location} Location object containing URL to check. Defaults
         *                   to window.location, used for testing.
         * @return {Boolean} True if the parameter was found and login failed,
         *                   False otherwise.
         */
        didLoginFail: function didLoginFail(location) {
            location = location || window_location;
            return location.search.indexOf('bid_login_failed=1') !== -1;
        },

        /**
         * Register callbacks with navigator.id.watch that make the API work.
         * This must be called before calling any other API methods.
         * @return {jqXHR} Deferred that resolves after the handlers have been
         *                 have been registered.
         */
        registerWatchHandlers: function registerWatchHandlers() {
            return django_browserid.getInfo().then(function(info) {
                navigator.id.watch({
                    loggedInUser: info.userEmail,
                    onlogin: function(assertion) {
                        // Avoid auto-login on failure.
                        if (!avoidedAutoLogin && django_browserid.didLoginFail()) {
                            navigator.id.logout();
                            avoidedAutoLogin = true;
                            return;
                        }

                        if (requestDeferred) {
                            requestDeferred.resolve(assertion);
                        }
                    },
                    onlogout: function() {
                        if (logoutDeferred) {
                            logoutDeferred.resolve();
                        }
                    }
                });
            });
        }
    };

    window.django_browserid = django_browserid;
})(window.jQuery, window.navigator, window.location);
