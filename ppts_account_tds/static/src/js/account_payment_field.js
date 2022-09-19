odoo.define('ppts_account_tds.account_payment_field', function(require) {
	"use strict";

	var AbstractField = require('web.AbstractField');
	var core = require('web.core');
	var field_registry = require('web.field_registry');
	var field_utils = require('web.field_utils');
	var QWeb = core.qweb;
	var ShowTdsLineWidget = AbstractField.extend({
		events : _.extend({
			'click .outstanding_credit_tds' : '_onOutstandingTdsAssign',
		}, AbstractField.prototype.events),
		supportedFieldTypes : [ 'char' ],

		_render : function() {
			var self = this;
			var info = JSON.parse(this.value);
			if (!info) {
				this.$el.html('');
				return;
			}
			this.$el.html(QWeb.render('ShowPaymentTds', {
				lines : info.content,
				outstanding : info.outstanding,
				title : info.title
			}));
			_.each(this.$('.js_tds_rec_info'), function(k, v) {
				var content = info.content[v];
				var options = {
					content : function() {
						var $content = $(QWeb.render('TdsPopOverRec', {
							name : content.name,
							code : content.code,
							currency : content.currency,
							tds_amount : content.tds_amount,
							bal_amount : content.bal_amount,
							tds_reconcile_id : content.id,
							invoice_id : content.invoice_id,
						}));
						return $content;
					},
					html : true,
					placement : 'right',
					title : 'TDS Information',
					trigger : 'focus',
					delay : {
						"show" : 0,
						"hide" : 100
					},
				};
				$(k).popover(options);
			});
		},
		_onOutstandingTdsAssign : function(event) {
			var self = this;
			var id = $(event.target).data('id') || false;
			this.do_action({
				type : 'ir.actions.act_window',
				res_model : 'tds.add.reconcile',
				view_mode : 'form',
				view_type : 'form',
				views : [ [ false, 'form' ] ],
				target : 'new',
				context : {
					'default_tds_line_id' : id
				}
			});
		},
	});
	field_registry.add('tds', ShowTdsLineWidget);

});
