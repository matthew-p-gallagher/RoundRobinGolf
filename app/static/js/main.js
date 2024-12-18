// Add CSRF token to all AJAX requests
$.ajaxSetup({
	beforeSend: function (xhr, settings) {
		if (!/^(GET|HEAD|OPTIONS|TRACE)$/i.test(settings.type) && !this.crossDomain) {
			xhr.setRequestHeader('X-CSRFToken', $('meta[name="csrf-token"]').attr('content'));
		}
	},
});
