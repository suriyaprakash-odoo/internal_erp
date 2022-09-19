/*global $, _, PDFJS */
odoo.define('crm_dashboard.crm_dashboard', function (require) {
"use strict";


var ajax = require('web.ajax');
var ControlPanelMixin = require('web.ControlPanelMixin');
var core = require('web.core');
var Dialog = require('web.Dialog');
var session = require('web.session');
var utils = require('web.utils');
var web_client = require('web.web_client');
var Widget = require('web.Widget');
var NotificationManager = require('web.notification').NotificationManager;
var rpc = require('web.rpc');

var _t = core._t;
var QWeb = core.qweb;

$(document).ready(function(){
    $("body").delegate("#team,#person", "change", function(result) {
    	var sales_person=$("#person").val();
    	localStorage.setItem("sales_person", sales_person);
    	new Dashboard();

  });
    $("body").delegate(".onclick_week", "click", function(result) {
    	var sales_person=$("#person").val();
    	localStorage.setItem("sales_person", sales_person);
    	
    	localStorage.setItem("week", 1);
    	new Dashboard();

  });
    $("body").delegate(".onclick_quarter", "click", function(result) {
    	var sales_person=$("#person").val();
    	localStorage.setItem("sales_person", sales_person);
    	
    	localStorage.setItem("quarter", 1);
    	new Dashboard();

  });
    $("body").delegate(".onclick_month", "click", function(result) {
    	var sales_person=$("#person").val();
    	localStorage.setItem("sales_person", sales_person);
    	
    	localStorage.setItem("month", 1);
    	new Dashboard();

  });
    
    $("body").delegate(".onclick_year", "click", function(result) {
    	var sales_person=$("#person").val();
    	localStorage.setItem("sales_person", sales_person);
    	
    	localStorage.setItem("year_click", 1);
    	new Dashboard();

  });
});

var Dashboard = Widget.extend(ControlPanelMixin, {
    template: "crm_dashboard.HomePage",
    searchview_hidden: true,

    events: {
        'click .o_dashboard_stage' :   'o_dashboard_stage_clicked'
    },

    o_dashboard_stage_clicked : function(ev) {
        ev.preventDefault();
        var $action = $(ev.currentTarget);
        var action_name = $action.attr('name');
        web_client.action_manager.do_action({
            name: action_name,
            views: [[false, 'list'],[false, 'form']],
            view_type: 'list',
            view_mode: 'list',
            domain: [['stage_id', '=', action_name]],
            res_model: 'crm.lead',
//            context:{search_default_assigned_to_me:'True'},

            type: 'ir.actions.act_window',
            target: 'current',
        });
    },

    init: function(parent, context) {
        this._super(parent, context);
        this.dashboards_templates = ['crm_dashboard.dashboard'];
        this.render_dashboards()
    },
    start: function() {
        var self = this;
        return this._super().then(function() {
            self.update_cp();
            self.render_dashboards();
            self.$el.parent().addClass('oe_background_grey');
        });
    },
    
    on_reverse_breadcrumb: function() {
        web_client.do_push_state({});
        this.update_cp();
    },

    //To update breadcrumbs
    update_cp: function() {
        var self = this;
        
        this.update_control_panel({
            cp_content: {
                $searchview: this.$searchview,
            },
            breadcrumbs: this.getParent().get_breadcrumbs(),
        });
    },

    // fetch_dashboard_data will contains all data related to dashboard

    
    render_dashboards: function() {

    	
    	var team = $( "#team" ).val();
	    var person = $( "#person" ).val();
	    var week =localStorage.getItem("week");
	    var quarter =localStorage.getItem("quarter");
	    var month =localStorage.getItem("month");
	    var year_click =localStorage.getItem("year_click");

   		localStorage.removeItem("week");
   		localStorage.removeItem("quarter");
   		localStorage.removeItem("month");
   		localStorage.removeItem("year_click");
        var self = this;

            _.each(this.dashboards_templates, function(template) {
            	rpc.query({
        	       
                    model: 'crm.dashboard',
                    method: 'fetch_dashboard_data',
                    args: [team,person,week,quarter,month,year_click],
                })
                .then(
               function(result){
            	   var sales_person=localStorage.getItem("sales_person");
                   if (sales_person != null){
                	   $('.o_website_dashboard').html("");
                	   $('.o_website_dashboard').append(QWeb.render(template, {widget: self,values: result,}));
                	   $( "#team" ).val(team);
                	   $( "#person" ).val(person);
                   }
                   if (sales_person == null){

                	   self.$('.o_website_dashboard').html("");
                	   self.$('.o_website_dashboard').append(QWeb.render(template, {widget: self,values: result,}));
                   }
               		localStorage.removeItem("sales_person");
              });
            });

        }
});
    core.action_registry.add('crm_dashboard', Dashboard);
    return Dashboard
    
});



