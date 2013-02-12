/* This Source Code Form is subject to the terms of the Mozilla Public
 * License, v. 2.0. If a copy of the MPL was not distributed with this
 * file, You can obtain one at http://mozilla.org/MPL/2.0/. */

(function($) {
    'use strict';

    $(function() {
        // State? Ewwwwww.
        var logoutUrl = null;
        var $loginButton = null;
        var loginFailed = location.search.indexOf('bid_login_failed=1') !== -1;

        $(document).on('click', '.browserid-login', function(e) {
            e.preventDefault();

            // Pull request arguments from the data-request-args attribute.
            $loginButton = $(this);
            navigator.id.request($loginButton.data('requestArgs'));
        });

        $(document).on('click', '.browserid-logout', function(e) {
            e.preventDefault();
            logoutUrl = $(this).attr('href');
            navigator.id.logout();
        });

        navigator.id.watch({
            loggedInUser: $('#browserid-info').data('userEmail') || null,
            onlogin: function(assertion) {
                // Avoid auto-login on failure.
                if (loginFailed) {
                    loginFailed = false;
                    return;
                }

                if (assertion && $loginButton) {
                    var $form = $loginButton.prev('.browserid-form');
                    assertion = assertion.toString();
                    $form.find('input[name="assertion"]').val(assertion);
                    $form.submit();
                }
            },
            onlogout: function() {
                // Follow the logout link's href once logout is complete.
                var currentLogoutUrl = logoutUrl;
                if (currentLogoutUrl !== null) {
                    logoutUrl = null;
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
