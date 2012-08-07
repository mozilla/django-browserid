/* This Source Code Form is subject to the terms of the Mozilla Public
 * License, v. 2.0. If a copy of the MPL was not distributed with this
 * file, You can obtain one at http://mozilla.org/MPL/2.0/. */
/* The persona documentation is at
 * https://developer.mozilla.org/en-US/docs/BrowserID/Quick_Setup
 * and requests that login and logout callbacks are included so
 * that accounts can be managed.
 */
 $(document).ready(function() {
    $('#browserid').bind('click', function(e) {
        e.preventDefault();
        navigator.id.request();
    };
    $('.logout').bind('click', function(e) {
        /* obviously, this should also be called for any other
         * logout like action. Standard action can be applied
         * before and after this call.
         */
        navigator.id.logout();
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
             * callback must be provided
             */
            if (typeof $e.parent().logout === 'function') {
                $e.parent().logout()
            }
        });
    });
});
