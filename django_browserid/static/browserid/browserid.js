/* This Source Code Form is subject to the terms of the Mozilla Public
 * License, v. 2.0. If a copy of the MPL was not distributed with this
 * file, You can obtain one at http://mozilla.org/MPL/2.0/. */
/* The BrowserID documentation is at
 * https://developer.mozilla.org/en-US/docs/BrowserID/Quick_Setup
 */
 $(document).ready(function() {
    $('.browserid-login').bind('click', function(e) {
        e.preventDefault();
        // Triggers BrowserID login dialog.
        navigator.id.request();
    };

    $('.browserid-logout').bind('click', function(e) {
        e.preventDefault();
        // Clears User Agent BrowserID state
        navigator.id.logout();
    };

    // Deprecated (Will be removed)
    $('#browserid').bind('click', function(e) {
        e.preventDefault();
        navigator.id.request();
    };

    navigator.id.watch(
        onlogin: function(assertion) {
            if (assertion) {
                var $e = $('#id_assertion');
                $e.val(assertion.toString());
                $e.parent().submit();
            }
        },

        onlogout: function() {
            /* no additional action required, however
             * callback must be provided to watch()
             */
            }
        });
    });
});
