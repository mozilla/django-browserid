/* This Source Code Form is subject to the terms of the Mozilla Public
 * License, v. 2.0. If a copy of the MPL was not distributed with this
 * file, You can obtain one at http://mozilla.org/MPL/2.0/. */

(function($) {
    'use strict';

    $(function() {
        // State? Ewwwwww.
        var loginRedirect = null; // Path to redirect to post-login.
        var logoutRedirect = null; // Path to redirect to post-logout.

        var $loginForm = $('#browserid-form'); // Form used to submit login.
        var $browseridInfo = $('#browserid-info'); // Useful info from backend.

        var requestArgs = $browseridInfo.data('requestArgs') || {};
        var loginFailed = location.search.indexOf('bid_login_failed=1') !== -1;

        // Call navigator.id.request whenever a login link is clicked.
        $(document).on('click', '.browserid-login', function(e) {
            e.preventDefault();

            loginRedirect = $(this).data('next');
            navigator.id.request(requestArgs);
        });

        // Call navigator.id.logout whenever a logout link is clicked.
        $(document).on('click', '.browserid-logout', function(e) {
            e.preventDefault();

            logoutRedirect = $(this).attr('href');
            navigator.id.logout();
        });

        navigator.id.watch({
            loggedInUser: $browseridInfo.data('userEmail') || null,
            onlogin: function(assertion) {
                // Avoid auto-login on failure.
                if (loginFailed) {
                    navigator.id.logout();
                    loginFailed = false;
                    return;
                }

                if (assertion) {
                    $loginForm.find('input[name="next"]').val(loginRedirect);
                    $loginForm.find('input[name="assertion"]').val(assertion);
                    $loginForm.submit();
                }
            },
            onlogout: function() {
                // Follow the logout link's href once logout is complete.
                var currentLogoutUrl = logoutRedirect;
                if (currentLogoutUrl !== null) {
                    logoutRedirect = null;
                    window.location = currentLogoutUrl;
                } else {
                    // Sometimes you can get caught in a loop where BrowserID
                    // keeps trying to log you out as soon as watch is called,
                    // and fails since the logout URL hasn't been set yet.
                    // Here we just find the first logout button and use that
                    // URL; if this breaks your site, you'll just need custom
                    // JavaScript instead, sorry. :(
                    currentLogoutUrl = $('.browserid-logout').attr('href');
                    if (currentLogoutUrl) {
                        window.location = currentLogoutUrl;
                    }
                }
            }
        });
    });
})(jQuery);
