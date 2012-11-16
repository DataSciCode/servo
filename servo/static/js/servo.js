/**
 * servo.js
 */
$(function() {
	$('input.filter').keyup(function() {
		var rex = new RegExp($(this).val(), 'i');
		$('.searchable tr').hide();
		$('.searchable tr').filter(function() {
		    return rex.test($(this).text());
		}).show();
	});

	$('#gsx-container').load($('#gsx-container').data('source'));

	$('.property:last select').live('change', function(e) {
        var newRow = $('.property:last').clone().insertAfter($('.property:last'));
        $(newRow).children('select').data('value', $(this).val());
        $('.property:last option:selected').next()
            .attr('selected', 'selected');
        $('.property:last input').val('').focus();
        $(this).val($(this).data('value'));
    });

	$('#id_sold_to').blur(function() {
	    if($('#id_ship_to').val() == '') {
	        $('#id_ship_to').val($('#id_sold_to').val());
	    }
	});

	loc = location.pathname.split("/")[1]
	$('#topnav > li > a[href*="' + loc + '"]').parent().addClass('active');
	$('.nav a[href="' + location.pathname + '"]').parent().addClass('active');

	$('#order-sidebar select').change(function(event) {
		t = $(event.currentTarget);
        url = t.parents('form').attr('action');
        arg = t.attr('name');
        args = {};
        args[arg] = t.val();
        
        $('#events').load(url, args, function() {
        	if (arg == "queue") {
        		console.log('reload statuses!');
            	$('#id_status').load('/orders/'+t.val()+'/statuses/');
        	};
        });
	});

    $('#template-select li a').click(function(e) {
        e.preventDefault();
        $('#body').load($(this).attr('href'));
        return false;
    });

    $('input.datepicker').datepicker();
    $('textarea:first').focus();

});
