$('#browserid').bind('click', function(e) {
    e.preventDefault();
    navigator.getVerifiedEmail(function(assertion) {
        if (assertion) {
            var $e = $('#id_assertion');
            $e.val(assertion.toString());
            $e.parent().submit();
        }
    });
});