/* This Source Code Form is subject to the terms of the Mozilla Public
 * License, v. 2.0. If a copy of the MPL was not distributed with this
 * file, You can obtain one at http://mozilla.org/MPL/2.0/. */

;(function($, navigator, window_location) {
    'use strict';

    // Public API
    var django_browserid = {
        /**
         * Retrieve an assertion and use it to log the user into your site.
         * @param {object} requestArgs Options to pass to navigator.id.request.
         * @param {string} next URL to redirect the user to if login is
         *                      successful.
         * @return {jQuery.Deferred} Deferred that resolves once the user has
         *                           been logged in.
         */
        login: function login(requestArgs, next) {
            if (typeof requestArgs === 'string') {
                next = requestArgs;
                requestArgs = undefined;
            }

            return django_browserid.getAssertion(requestArgs).then(function(assertion) {
                return django_browserid.verifyAssertion(assertion, next);
            });
        },

        /**
         * Log the user out of your site.
         * @param {string} next URL to redirect the user to if logout is
         *                      successful.
         * @return {jQuery.Deferred} Deferred that resolves once the user has
         *                           been logged out.
         */
        logout: function logout(next) {
            var info = this.getInfo();
            return this.getCsrfToken().then(function(csrfToken) {
                return $.ajax(info.logoutUrl, {
                    type: 'POST',
                    data: {next: next},
                    headers: {'X-CSRFToken': csrfToken},
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
            requestArgs = $.extend({}, this.getInfo().requestArgs, requestArgs);

            this._requestDeferred = $.Deferred();
            navigator.id.request(requestArgs);
            return this._requestDeferred;
        },

        /**
         * Verify that the given assertion is valid, and log the user in.
         * @param {string} assertion Assertion to verify.
         * @param {string} next URL to redirect the user to if the assertion is
         *                      valid.
         * @return {jQuery.Deferred} Deferred that resolves with the login view
         *                           response once login is complete.
         */
        verifyAssertion: function verifyAssertion(assertion, next) {
            var info = this.getInfo();
            return this.getCsrfToken().then(function(csrfToken) {
                return $.ajax(info.loginUrl, {
                    type: 'POST',
                    data: {assertion: assertion, next: next},
                    headers: {'X-CSRFToken': csrfToken},
                });
            });
        },

        // Cache for the info fetched by django_browserid.getInfo().
        _info: null,

        /**
         * Fetch the info for the Persona popup and login requests.
         * @return {object} Data encoded in the browserid-info tag.
         */
        getInfo: function getInfo() {
            if (!this._info) {
                this._info = $('#browserid-info').data('info');
            }

            return this._info;
        },

        /**
         * Fetch a CSRF token from the backend.
         * @return {jqXHR} jQuery XmlHttpResponse that returns the token.
         */
        getCsrfToken: function getCsrfToken() {
            return $.get(this.getInfo().csrfUrl);
        },

        // Deferred for post-watch-callback actions.
        // Stored on the public API so tests can reset it.
        _requestDeferred: null,

        /**
         * Register callbacks with navigator.id.watch that make the API work.
         * This must be called before calling any other API methods.
         * @param {function} Function to run once the user agent is ready to
         *                   process login requests.
         */
        registerWatchHandlers: function registerWatchHandlers(onReady) {
            var assertion = null;
            var self = this;

            navigator.id.watch({
                onlogin: function(assertion) {
                    if (self._requestDeferred) {
                        self._requestDeferred.resolve(assertion);
                    }
                },
                onready: onReady,
            });
        }
    };

    window.django_browserid = django_browserid;
})(window.jQuery, window.navigator, window.location);
