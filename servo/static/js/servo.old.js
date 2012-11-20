/**
 * @file servo/public/js/servoapp.js
 * @copyright 2011 Filipp Lepalaan
 * http://documentcloud.github.com/backbone/
 * http://documentcloud.github.com/underscore/
 */

var TabView = Backbone.View.extend(
{
    el: "div.tabView"
,
    events: {
        "click .tabs li a"      : "clicked"
    }
,
    clicked: function(event)
    {
        event.preventDefault();
        var el = event.currentTarget;
        this.$("ul.tabs li a").removeClass("active");
        this.$(el).addClass("active");
        this.$(".tab").hide();
        var tab = $(el).attr("href");
        this.$(tab).show();
    }
,
    render: function()
    {
        this.$(".tab").hide();
        this.$(".tabs li a").removeClass("active");
        this.$(".tabs li:first a").addClass("active");
        
        var first = this.$(".tabs li:first a").attr("href");

        $(first).show();

        this.$(".tabs li:first a").css(
            "border-left", "1px solid #222"
        );
        this.$(".tabs li:first a").css(
            "border-top-left-radius", "3px"
        );
        this.$(".tabs li:first a").css(
            "border-bottom-left-radius", "3px"
        );
        this.$(".tabs li:last a").css(
            "border-right", "1px solid #222"
        );
        this.$(".tabs li:last a").css(
            "border-top-right-radius", "3px"
        );
        this.$(".tabs li:last a").css(
            "border-bottom-right-radius", "3px"
        );
        return this;
    }
});

var PanelView = Backbone.View.extend(
{
    el: "div#popup"
,
    events: {
        "click .save"           : "submit",
        "click .cancel"         : "hidePanel",
        "click .searchSource a" : "setSource",
        "submit #drawer form"   : "lookup",
    }
,
    setSource: function(event)
    {
        var url = $(event.currentTarget).data("url");
        $("#searchForm").attr("action", url);
    }
,
    lookup: function(event)
    {
        event.preventDefault();
        var form = event.currentTarget;
        var url = $(form).attr("action");
        var tab = $("#drawer .tab:visible");
        
        if(tab.length < 1) {
            var tab = "#localResults";
        }
        
        this.$(tab).text("Loading…");
        $(tab).load(url, {q: $('#searchQuery').val()});
    }
,
    loadUrl: function(url)
    {
        $(window).scrollTop(0);
        this.$(".content").load(url, this.showPanel);
    }
,
    showPanel: function()
    {
        var popup = $(this).parent();
        window.tabView = new TabView();
        tabView.render();
        
        if(popup.is(':hidden'))
        {
            $('.popup-menu').hide();
            popup.show('slide', {direction: 'up'}, 200,
            
            function() {
                $('#popup #drawer').hide();
                
                $('#popup a.search').click(function()
                {
                    // load the search drawer
                    $('#drawer').load($(this).data('url'), function()
                    {
                        tabView2 = new TabView({el: 'div.searchTab'});
                        tabView2.render();
                        window.panelView.render();
                        window.panelView.delegateEvents();
                    });
                    
                    $(this).toggleClass('active');
                    $('#drawer').toggle('slide', 'fast');
                    
                });
            });
        }
    }
,
    hidePanel: function()
    {
        if(this.$el.is(":visible")) {
            this.$el.hide("slide", {direction: "up"}, 200);
            $("#pager_msg").text("");
        }
    }
,
    submit: function(event)
    {
        event.preventDefault();
        var form = $("#popup form");
        var reload = "#" + $(form).attr("rel");

        $.ajax(
        {
            type: "POST",
            data: $(form).serialize(),
            url: $(form).attr("action"),

            complete: function(data, json) {
                console.log(data);
                $("#pager_spinner").hide()
            }
,
            error: function(resp, status, data) {
                console.log(status)
                if(status == 302) {
                    window.location.replace(json.redirect);
                    return false;
                }
                $('#status_bar').html(resp.responseText).fadeIn();
            }
,
            success: function(response) {
                console.log(response);
                // reload only the relevant portion of the page
                $(reload).load($(reload).data("url"),
                    function() {
                        window.tableView.render();
                        window.panelView.hidePanel();
                });
            }
        });
    }
});

var AppView = Backbone.View.extend(
{
    el: "#page"
,
    events: {
        "keydown"			    : "closePanel",
        "click .popup"         : "runPanel",
        "click a.window"        : "openWindow",
        "click #pager a.button" : "hidePager",
        "ajaxStart"             : "ajaxStart",
        "ajaxStart"             : "ajaxStart",
        "ajaxStop"              : "ajaxStop",
    }
,
    ajaxStop: function()
    {
      $("#pager_spinner").hide();
    }
,
    ajaxStart: function()
    {
      // global handler for Ajax request starts
      $("#pager_spinner").show();
    }
,
    hidePager: function()
    {
        $("#pager").slideUp();
    }
,
    openWindow: function(event)
    {
        event.preventDefault();
        var url = $(event.currentTarget).attr("href");
        window.open(url);
    }
,
    // Escape key closes popup panel
    closePanel: function(event)
    {
        if(event.keyCode == 27) {
            event.preventDefault();
            window.panelView.hidePanel();
        }
    }
,
    runPanel: function(event)
    {
        $('#status_bar').hide();
        event.preventDefault();
        var url = $(event.currentTarget).attr("href");
        
        if(!url) {
            url = $(event.currentTarget).data('url');
        }

        if(url != "javascript:;") {
            $('#toolbar li > ul').fadeOut();
            window.panelView.loadUrl(url);
            $("#toolbar .menu li ul").fadeOut("fast");
        }
    }
,
    initialize: function()
    {
        // initialize subviews
        window.contentView = new ContentView();
        window.toolbarView = new ToolbarView();
        
        window.tableView = new TableView();
        window.listView = new ListView();

        window.panelView = new PanelView();
        window.sidebarView = new SidebarView();

        // preload some images
        var preloadImages = ["action.png", "action-active.png", "work.png",
            "home.png", "checkbox-checked.png", "checkbox-inactive.png",
            "todo.png", "todo-done.png", "radio.png", "radio-active.png", 
            "30/filter-active.png", "searchable-right.png",
            "searchable-right-active.png"];

        for( var i = preloadImages.length - 1; i >= 0; i-- ){
//            (new Image()).src = "/static/images/dark/" + preloadImages[i];
        };

        (new Image()).src = "/static/images/packed.png";
        (new Image()).src = "/static/images/packed-bg.png";

    }
});

var ToolbarView = Backbone.View.extend(
{
    el: "div#toolbar"
,
    initialize: function() {
        $("#new_tag").autocomplete({
            source: "/tags/order",
            select: function(event, ui) {
                //console.log(event, ui);
                $.post("/orders/3/tags/new", {'title': ui.item.value});
            }
        });
    }
,
    events: {
        "keyup #query"              : "smartSearch",
        "click .shownext"           : "togglePopup",
        "click .button"             : "buttonClicked",
        "click .filterProducts"     : "filterProducts",
        "click ul > li a.enabled"   : "toggleMenu"
    }
,
    smartSearch: function(event)
    {
        if(event.keyCode != 13) {
            return false
        }

        q = $(event.currentTarget).val().trim();

        if(q.match(/^\d{6}$/)) {
            window.location = '/orders/'+q;
        }
        if(q.match(/^[a-z0-9]{11,12}$/i)) {
            window.location = '/device/'+q;
        }

    }
,
    togglePopup: function(event)
    {
        event.preventDefault();
        $(event.currentTarget).next('.popup-menu').toggle();
    }
,
    buttonClicked: function(event)
    {
        var t = $(event.currentTarget);
        if(!t.hasClass('shownext') && !t.hasClass('popup')) {
            console.log('buttonclick in toolbar');
            window.location = $(event.currentTarget).data('url');
        }
    }
,
    showMenu: function(event)
    {
        this.$("li > ul").hide();
    }
,
    toggleMenu: function(event)
    {
        $(event.currentTarget).next("ul").fadeToggle("fast");
    }
,
    filterProducts: function(event)
    {
        var checked = $(event.currentTarget).prop("checked");
        
        if(event.altKey) {
            $(".filterProducts").prop("checked", checked);
        }
        
        // collect the selected tags
        var tags = $(".filterProducts:checked").map(function() {
            return this.value;
            }).get();
        
        $("#products").load("/products/index", {tags: tags});
    }
});

var TableView = Backbone.View.extend(
{
    el: "div.tableView"
,
    initialize: function() {
        this.id = null;
        this.collection = null;
        this.noPopup = ["orders"];
        this.render();
    }
,
    events: {
        "dblclick tbody tr"   : "open",
        "click a.action"      : "toggleDropdown"
    }
,
    toggleDropdown: function(e)
    {
        console.log("toggleDropdown!");
        e.preventDefault();
        $(e.currentTarget).next().toggle();
    }
,
    reload: function() {
        var url = $(this).attr("data-url");
        $(this).load(url);
    }
,
    shouldPopup: function() {
        return (this.noPopup.indexOf(this.collection) == -1);
    }
,
    open: function(event) {
        event.preventDefault();
        var url = $(event.currentTarget).data('url');        
        panelView.loadUrl(url);
    }
});

/**
 * SidebarView represents the whole sidebar
 */
var SidebarView = Backbone.View.extend(
{
    el: "div#side_pane"
,
    events: {
        "click .save"		: "submit",
        "click .follow"	    : "follow",
        "click .head"		: "toggle",
        "change select"		: "update_order",
        //"click ul li ul li" : "select",
    }
,
    initialize: function()
    {
        var hidden = $('body').data('hidden');
        $(hidden).toggleClass("closed").next().toggle();
        this.$(".draggable").draggable(
            {revert: "invalid"}
        );
        
        this.$(".draggable").droppable({
            revert: "invalid",
            drop: function(event, ui) {
                console.log(event, ui);
                var url = ui.draggable.attr('href');
                var id = url.split('/').pop();
                $.get('/search/'+id+'/remove');
                ui.draggable.remove();
            }
        }
        );
    }
,
    follow: function(event)
    {
        event.preventDefault();
        var target = event.currentTarget;
        var url = $(target).attr('href');
        $(".follow span").load(url, function() {
            $(target).toggleClass("active");
            $(target).attr("href", url.replace("follow", "unfollow"));
        });
    }
,
    submit: function(event) {
        var url = $("#miniform").attr("action");
        $.post(url, $("#miniform").serialize(), function()
        {
            $("#minimessage").val("");
            $("#notes").load($("#notes").data("url"));
        });
    }
,
    toggle: function(event)
    {
        var ul = $(event.currentTarget).toggleClass("closed")
            .next().toggle();
    }
,
    update_order: function(event)
    {
        t = $(event.currentTarget);
        url = t.parents('form').attr('action');
        arg = t.attr('name');
        args = {};
        args[arg] = t.val();
        console.log(url)
        $('#events').load(url, args);
        if (arg == "queue") {
            $('#select_status').load('/orders/statuses')
            console.log('reload statuses!');
        };
    }
,
    select: function(event)
    {
        event.preventDefault();
        var li = event.currentTarget;
        this.$('ul li').removeClass('current');
        $(li).addClass('current');

        var url = $(li).children('a').attr('href');
        $("head > title").text($(li).children("a").text());
        window.app.navigate(url , true);
    }
});

var ContentView = Backbone.View.extend(
{
    el: "div#main_content"
,
    events: {
        "click .tableView tbody tr" : "selectRow",
        "click a.async"             : "goto",
    }
,
    goto: function(event)
    {
        $.get($(event.currentTarget).attr("href"));
        event.preventDefault();
    }
,
    selectRow: function(event)
    {
        this.$('.current').removeClass('current');
        
        var row = event.currentTarget;
        
        $(row).addClass("current");

        $('.delete').removeClass('disabled').addClass('popup');

        var url = $(row).data("url");
        results = url.match(/\d+/);
        id = results[0]
        console.log(url);
        
        $('#note-actions a').map(function(e)
        {
            href = $(this).attr('href');
            href = href.replace(/\d+/, id);
            $(this).attr('href', href).addClass('enabled');
        });

        $('.delete').data('url', url.replace(/(\d+)/, '$1/remove'));

    }
,
    load: function(url) {
        url = url.replace(/^\//, '');
        $(this.el).load("/" + url, function() {
            window.tableView = new TableView();
            window.listView = new ListView();
//            tabView.render();
        });
    }
});

var ListView = Backbone.View.extend(
{
	el: 'div.listView'
,
	initialize: function() {
		//var first = this.$("> ul li:first");
		//$(first).addClass("current");
//		var url = first.children("a").attr("href");
	},
    
	events: {
        'click ul li'		: 'select',
        'dblclick ul li'    : 'open'
	}
,
    open: function(event) {
        var url = $(event.currentTarget).data('url');        
        panelView.loadUrl(url);
    }
,
	render: function()
	{
		this.$('ul > li:even').css('background-color', '#252525');
		return this;
	}
,
	shouldPopup: function() {
		return (this.noPopup.indexOf(this.collection) == -1);
	}
,
	select: function(event)
	{
		var e = event.currentTarget;
        $(e).siblings().removeClass('current');
		$(e).addClass('current');
        
        //var url = $(e).data('url');
        //remove_url = url.replace(/(\d+)/, '$1/remove');

        $('#delete-button').removeClass('disabled');
        $('#delete-button').addClass('enabled');
        $('#edit-button').removeClass('disabled');
        $('#edit-button').addClass('enabled');
        $('#delete-button').data('url', remove_url);
        $('#edit-button').data('url', remove_url.replace('/remove', '/edit'));
        // @todo: this slows Safari down to a crawl
		//$('#delete-button').removeClass('disabled');
		
		//$('#detailView').load(url);
		//window.app.navigate(url, true);
	}
	
});

var DetailView = ContentView.extend(
{
    el: "div#detailView"
});

var ServoApp = Backbone.Router.extend(
{
    initialize: function()
    {
        window.appView = new AppView();
    }
,
    defaultRoute: function(url)
    {
        if(url.match(/\d/)) {
            detailView = new DetailView();
            return this.detailRoute(url);
        }
        console.log("defaultRoute", url);
        contentView.load(url);
        contentView.delegateEvents();
	}
,
    detailRoute: function(url)
    {
        console.log("load detailview:", url);
        detailView.load(url);
        return false;
    }
,
    routes: {
        "*url"                  : "defaultRoute",
    }
});