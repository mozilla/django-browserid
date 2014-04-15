/* This Source Code Form is subject to the terms of the Mozilla Public
 * License, v. 2.0. If a copy of the MPL was not distributed with this
 * file, You can obtain one at http://mozilla.org/MPL/2.0/. */

;(function($, window) {
    'use strict';

    // Some platforms (Windows Phone and Chrome for iOS thusfar) require Persona
    // to use redirects instead of popups. Thus, while I'd like to ignore all
    // onlogin calls that don't happen after the user clicks a login link, we
    // have to for login to work on those platforms.
    // Solution? Store state in sessionStorage, which persists per-tab. Then we
    // can still support user-triggered logins across the redirect flow without
    // having other open tabs trigger auto-login.
    function onAutoLogin(assertion) {
        if (window.sessionStorage.browseridLoginAttempt === 'true') {
            window.sessionStorage.browseridLoginAttempt = 'false';
            django_browserid.verifyAssertion(assertion).then(function(verifyResult) {
                window.location = verifyResult.redirect;
            });
        }
    }

    /**
     * Compare the given URL to the current page's URL to see if they share the
     * same origin.
     */
    function matchesCurrentOrigin(url) {
        var a = document.createElement('a');
        a.href = url;
        var hostMatch = !a.host || window.location.host === a.host;
        var protocolMatch = !a.protocol || window.location.protocol === a.protocol;
        return hostMatch && protocolMatch;
    }

    $(function() {
        django_browserid.registerWatchHandlers(onAutoLogin);

        // Trigger login whenever a login link is clicked, and redirect the user
        // once it succeeds.
        $(document).on('click', '.browserid-login', function(e) {
            e.preventDefault();
            var $link = $(this);
            window.sessionStorage.browseridLoginAttempt = 'true';
            django_browserid.login().then(function(verifyResult) {
                window.sessionStorage.browseridLoginAttempt = 'false';
                var redirect = $link.data('next') || verifyResult.redirect;
                if (matchesCurrentOrigin(redirect)) {
                    window.location = redirect;
                }
            });
        });

        // Trigger logout whenever a logout link is clicked, and redirect the
        // user once it succeeds.
        $(document).on('click', '.browserid-logout', function(e) {
            e.preventDefault();
            var $link = $(this);
            django_browserid.logout().then(function(logoutResult) {
                var redirect = $link.attr('next') || logoutResult.redirect;
                if (matchesCurrentOrigin(redirect)) {
                    window.location = redirect;
                }
            });
        });
    });
})(jQuery, window);
