/**
 * servo.js
 */
$(function() {

    $('.toggle_column').click(function() {
        var checked = $(this).prop('checked');
        $('tbody input[type="checkbox"]').prop('checked', checked);
        $('button[type="submit"]').attr('disabled', !checked);
    });

    $('.toggle_row').click(function() {
        $(this).parents('tr').toggleClass('muted');
        // retabulate form
        var total_net = 0;
        var total_tax = 0;
        var total_gross = 0;

        _.each($('tbody tr:not(.muted)'), function(e) {
            amount = parseInt($(e).children('.amount').text());
            total_net += parseFloat($(e).children('.net').text()) * amount;
            total_tax += parseFloat($(e).children('.tax').text()) * amount;
            total_gross += parseFloat($(e).children('.gross').text()) * amount;
        });

        $('#total_net').val(total_net.toFixed(2));
        $('#total_tax').val(total_tax.toFixed(2));
        $('#total_gross').val(total_gross.toFixed(2));

    });

    _.each($('a.counter'), function(i, e) {
        $.get($(i).attr('href'), function(count) {
            $('<span class="badge pull-right"/>').text(count).appendTo(i);
            $('#topnav a.counter span.badge').addClass('badge-inverse');
        });
    });

    $('.copy-target').focus(function() {
        if($(this).val() == '') {
            $(this).val($('.copy-source').val());
        }
    });

    if ($('textarea').length) {
        $.get('/notes/templates/', function(r) {
            _.each($('.template'), function(e) {
                var label = $(e).parents('.control-group').children('.control-label');
                var text = label.text();
                label.replaceWith(_.template(r, {'title': text}));
            });
        });
    }

    if($('.progress .bar').length) {
        window.setInterval(function() {
            var p = parseInt($('.progress .bar').data('progress')) + 10;
            if(p < 100) {
                $('.progress .bar').data('progress', p).css('width', p+'%')
            }
        }, 500);
    }

    $('a.nofollow').click(function(e) {
        var that = $(this);
        $.get($(that).attr('href'), function(r) {
            $(that).text(r);
        });
        e.preventDefault();
    });

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

    $('#topnav>li>a[href*="'+loc+'"]').parent().addClass('active');
    $('.nav a[href="'+location.pathname+'"]').parent().addClass('active');

    $('#order-sidebar select').change(function(event) {
        t = $(event.currentTarget);
        url = t.parents('form').attr('action');
        arg = t.attr('name');
        args = {};
        args[arg] = t.val();

        $('#events').load(url, args, function() {
            if (arg == 'queue') {
                $('#id_status').load('/orders/'+t.val()+'/statuses/');
            };
        });
    });

    $('.template-select li a').live('click', function(e) {
        e.preventDefault();
        $(this).parent().dropdown('toggle');
        var target = $(this).closest('.control-group').find('textarea');
        $(target).load($(this).attr('href'));
        return false;
    });

    $('input.datepicker').datepicker();

    $('.typeahead').typeahead({
        source: function(query, process) {
            query = query.split(',').pop();
            $.get('/customers/search/', {'query': query}, function(r) {
                process(r);
            });
        }
    });

    $('textarea:first').focus();
    
});
