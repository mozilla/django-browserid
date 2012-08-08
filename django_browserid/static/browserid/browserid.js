/* This Source Code Form is subject to the terms of the Mozilla Public
 * License, v. 2.0. If a copy of the MPL was not distributed with this
 * file, You can obtain one at http://mozilla.org/MPL/2.0/. */

/* The BrowserID documentation is at
 * https://developer.mozilla.org/en-US/docs/BrowserID/Quick_Setup
 */
 $(document).ready(function() {
    $('.browserid-login, #browserid').bind('click', function(e) {
        e.preventDefault();
        navigator.id.request(); // Triggers BrowserID login dialog.
    });

    $('.browserid-logout').bind('click', function(e) {
        e.preventDefault();
        navigator.id.logout(); // Clears User Agent BrowserID state.
    });

    navigator.id.watch({
        onlogin: function(assertion) {
            if (assertion) {
                var $e = $('#id_assertion');
                $e.val(assertion.toString());
                $e.parent().submit();
            }
        },

        onlogout: function() {
            // TODO: Detect if logout button was a link and follow its href
            // if possible.
        }
    });
});
