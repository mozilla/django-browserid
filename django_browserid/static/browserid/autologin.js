/* This Source Code Form is subject to the terms of the Mozilla Public
 * License, v. 2.0. If a copy of the MPL was not distributed with this
 * file, You can obtain one at http://mozilla.org/MPL/2.0/. */

;(function(django_browserid) {
    'use strict';

    // Mock out django_browserid functions so that they avoid calling
    // navigator.id functions.
    django_browserid.login = function autoLogin(requestArgs, next) {
        if (typeof requestArgs === 'string') {
            next = requestArgs;
        }

        return django_browserid.verifyAssertion('fake', next);
    };

    django_browserid.registerWatchHandlers = function() {};
})(window.django_browserid);
