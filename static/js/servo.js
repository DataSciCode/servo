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
        "click .tabs li a"         : "clicked"
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
        var form = event.currentTarget;
        var url = $(form).attr("action");
        var tab = $("#drawer .tab:visible");
        if(tab.length < 1) {
            var tab = "#localResults";
        }
        console.log(tab);
        this.$(tab).text("Loading…");
        $(tab).load(url, $(form).serialize());
        event.preventDefault();
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
        
        if(popup.is(":hidden"))
        {
            popup.show("slide", {direction: "up"}, 200,
            
            function() {
                $("#popup #drawer").hide();
                
                $("#popup a.search").click(function()
                {
                    // load the search drawer
                    $("#drawer").load($(this).data("url"), function() {
                        tabView2 = new TabView({el: "div.searchTab"});
                        tabView2.render();
                        window.panelView.render();
                        window.panelView.delegateEvents();
                    });
                    
                    $(this).toggleClass("active");
                    $("#drawer").toggle("slide", "fast");
                    
                });       
                
            });
        }
    }
,
    hidePanel: function()
    {
        if(this.$el.is(":visible")) {
            this.$el.hide("slide", { direction: "up" }, 200 );
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
            url: $(form).attr("action"),
            data: $(form).serialize(),

            complete: function(data, json) {
                console.log(data, json);
            },

            error: function(data) {
                console.log(data);
                json = JSON.parse(data.responseText);
                
                if(data.status == 302) {
                    window.location.replace(json.redirect);
                    return false;
                }
                
                var badField = document.getElementById(json.badfield);
                $('<div class="error"></div>')
                    .html('<span>'+json.message+'</span>')
                    .insertAfter(badField)
                    .fadeIn();
            }
,
            success: function(data, status, json) {
                console.log(data);
/*                var j = JSON.parse(json.responseText);
                
                if(j.redirect) {
                    window.location.replace(j.redirect);
                    return false;
                }
*/
                $("#pager_msg").text(json.responseText);
                $("#pager").slideDown();
                window.panelView.hidePanel();
                
                // reload only the relevant portion of the page
                $(reload).load($(reload).attr("data-url"),
                    function() {
                        window.tableView.render();
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
        "click a.popup"		    : "runPanel",
        "click a.window"	    : "openWindow",
        "click #pager a.button" : "hidePager"
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
        event.preventDefault();
        var url = $(event.currentTarget).attr("href");
        if(url != "javascript:;") {
            window.panelView.loadUrl(url);
            $("#toolbar .menu li ul").fadeOut("fast");
        }
    }
,
    initialize: function()
    {
        window.panelView = new PanelView();
        window.sidebarView = new SidebarView();

        // preload some images
        var preloadImages = ["action.png", "action-active.png", "work.png",
            "home.png", "checkbox-checked.png", "checkbox-inactive.png",
            "todo.png", "todo-done.png", "radio.png", "radio-active.png", 
            "filter.png", "filter-active.png", "30/filter.png",
            "30/filter-active.png", "searchable-right.png",
            "searchable-right-active.png"];

        for( var i = preloadImages.length - 1; i >= 0; i-- ){
            (new Image()).src = "/static/images/dark/" + preloadImages[i];
        };

        (new Image()).src = "/static/images/moonkit/button.png";
        (new Image()).src = "/static/images/moonkit/button-hover.png";
        (new Image()).src = "/static/images/moonkit/button-active.png";

    }
});

var ToolbarView = Backbone.View.extend(
{
    el: "div#toolbar"
,
    initialize: function()
    {
        this.setElement('div#toolbar');
    }
,
    render: function()
    {
        $(this.el).html(Mustache.render(
            $('#toolbar-template').html(),
            this.model.get('items')
        ));
        return this;
    }
,
    events: {
        "submit #search"        : "search",
        "click .filterProducts" : "filterProducts",
        "click .menu > li > a"  : "toggleMenu"
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
,
    search: function(event) {
        $(event).preventDefault();
        var q = $("#search_query").val();
//        window.app.navigate( "/search/"+q+"/spotlight", true );
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
        "dblclick tbody tr"   : "open"
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
        "click .follow"		: "follow",
        "click .head"		: "toggle",
        "change select"		: "trigger_event",
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
                ui.draggable.fadeOut("fast");
                var url = ui.draggable.attr("href");
                var id = url.split("/").pop();
                $.post("/search/remove", {_id: id});
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
            $("#messages").load($("#messages")
                .attr("data-url"));
        });
    }
,
    toggle: function(event)
    {
        var ul = $(event.currentTarget).toggleClass("closed")
            .next().toggle();
        var id = $(event.currentTarget).attr("id");
        
        var hiddenItems = localStorage.getItem("hiddenSidebarItems");
        
        if(hiddenItems.typeof != 'array') {
            hiddenItems = new Array()
        }
        
        if(idx = hiddenItems.indexOf(id)) { // already hidden, unhide
            hiddenItems = hiddenItems.splice(idx, 1);
        } else {
            hiddenItems.push(id);
        }
        
        localStorage.setItem("hiddenSidebarItems", hiddenItems);
        
    }
,
    trigger_event: function(event)
    {
        var id = $(event.currentTarget).val();
        var type = $(event.currentTarget).attr("name");

        var reload = (type == "set_queue") ? "#set_status" : "#events";

        $(reload).load("/event/trigger/type/"+type+"/id/"+id, {
            id: id,
            type: type
        }, function() {
            $("#events").load($("#events").attr("data-url"));
        });
    }
,
    select: function(event)
    {
        event.preventDefault();
        var li = event.currentTarget;
        this.$("ul li").removeClass("current");

        var a = $(li).children("a");
        var url = a.attr("href");
        url = url.replace(/^\//, "");
        window.collection = url.slice(0, url.indexOf("/"));
        console.log(url, collection);
        $("#secondary").html("");
//        window.app.navigate( url , true );

        $("#edit-button").addClass("disabled");
        $("#delete-button").addClass("disabled");

        $("head > title").text(a.text());

        $(li).addClass("current");

    }
});

var ContentView = Backbone.View.extend(
{
    el: "div#main_content"
,
    events: {
        "click .tableView tbody tr" : "selectRow",
        "click a.async" : "goto",
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
        this.$(".current").removeClass("current");
        
        var row = event.currentTarget;
        
        $(row).addClass("current");

        this.collection = $(row).parent("tbody")
            .data("collection");

        this.collection = (this.collection)
            ? this.collection
            : window.collection;

        this.editAction = $(row).data("action");
        if(!this.editAction) this.editAction = "edit";

        this.id = $(row).data("id");
        this.deleteAction = "remove";
        this.item = $(row).data("item");

        if(this.item) {
            this.editAction += "-" + this.item;
            this.deleteAction += "-" + this.item;
        }

        $("#delete-button").removeClass("disabled")
            .addClass("popup");

        var url = $(row).data("url");
        
        $("#edit-button").attr("href", url);
        $(".reply").attr("href", url.replace("/edit/", "/reply/"));
        $("#delete-button").attr("href", url.replace("/edit", "/remove"));
        $("#edit-button").removeClass("disabled");
		
//		if( this.shouldPopup() ) {
			$("#edit-button").addClass( "popup" );
//		}

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
	el: "div.listView"
,
	initialize: function() {
//		var first = this.$("> ul li:first");
//		$(first).addClass("current");
//		var url = first.children("a").attr("href");
	},
    
	events: {
        "click ul li"		: "select"
	}
,
	render: function()
	{
		this.$("ul > li:even").css("background-color", "#252525");
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
		this.$("li").removeClass("current");
		$(e).addClass("current");
        
        var url = $(e).data("url");
        
        $("#delete-button").attr("href",
            url.replace(/^\/(\w+)\/\w+/, '/$1/remove')
        );
            
		$("#delete-button").removeClass("disabled");
		
        $("#edit-button").attr("href",
            url.replace(/^\/(\w+)\/\w+/, '/$1/edit')
        );
        
		$("#edit-button").addClass("popup");
		
		$('#detailView').load(url);
//		window.app.navigate(url, true);
	}
	
});

var DetailView = Backbone.View.extend(
{
	el: "div.detailView"
});

var ServoApp = Backbone.Router.extend(
{
    initialize: function()
    {
        window.appView = new AppView();
        window.contentView = new ContentView();
        window.toolbarView = new ToolbarView();
        
        window.tableView = new TableView();
        window.listView = new ListView();
    }
,
    goto: function(url)
    {
        console.log("goto", url);
        parts = url.split(/\//);
//        contentView.load(url);
        contentView.delegateEvents();
	}
,
    routes: {
        "*url"			: "goto",
    }
});
