/* This Source Code Form is subject to the terms of the Mozilla Public
 * License, v. 2.0. If a copy of the MPL was not distributed with this
 * file, You can obtain one at http://mozilla.org/MPL/2.0/. */

;(function($, window) {
    'use strict';

    $(function() {
        django_browserid.registerWatchHandlers().then(function() {
            // Trigger login whenever a login link is clicked, and redirect the user
            // once it succeeds.
            $(document).on('click', '.browserid-login', function(e) {
                e.preventDefault();
                var $link = $(this);
                django_browserid.login().then(function(verifyResult) {
                    window.location = $link.data('next') || verifyResult.redirect;
                });
            });

            // Trigger logout whenever a logout link is clicked, and redirect the
            // user once it succeeds.
            $(document).on('click', '.browserid-logout', function(e) {
                e.preventDefault();
                var $link = $(this);
                django_browserid.logout().then(function(logoutResult) {
                    window.location = $link.attr('next') || logoutResult.redirect;
                });
            });
        });
    });
})(jQuery, window);
