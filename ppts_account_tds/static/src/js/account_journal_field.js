odoo.define('ppts_account_tds.account_journal_field', function(require) {
	"use strict";

	var AbstractField = require('web.AbstractField');
	var core = require('web.core');
	var field_registry = require('web.field_registry');
	var field_utils = require('web.field_utils');
	var QWeb = core.qweb;
	var ShowTdsJournalWidget = AbstractField.extend({
		_render : function() {
			var self = this;
			var info = JSON.parse(this.value);
			if (!info) {
				this.$el.html('');
				return;
			}
			this.$el.html(QWeb.render('ShowJournalTds', {
				lines : info.content,
				outstanding : info.outstanding,
				id : info.id,
				title : info.title
			}));
			_.each(this.$('.js_tds_info'), function(k, v) {
				var content = info.content[v];
				var options = {
					content : function() {
						var $content = $(QWeb.render('TdsPopOver', {
							name : content.name,
							currency : content.currency,
							reconcile_amount : content.reconcile_amount,
							tds_reconcile_id : content.id,
							invoice_id : content.invoice_id,
						}));
						$content.filter('.js_unreconcile_tds').on('click',
								self._onRemoveTdsReconcile.bind(self));
						return $content;
					},
					html : true,
					placement : 'left',
					title : 'Reconcile Payment',
					trigger : 'focus',
					delay : {
						"show" : 0,
						"hide" : 100
					},
				};
				$(k).popover(options);
			});
		},
		_onRemoveTdsReconcile : function(event) {
			var self = this;
			var paymentId = parseInt($(event.target).attr("tds_reconcile_id"));
			if (paymentId !== undefined && !isNaN(paymentId)) {
				this._rpc({
					model : 'account.invoice',
					method : 'remove_tds_reconcile',
					args : [ 1,paymentId ]
				}).then(function() {
					self.trigger_up('reload');
				});
			}
		},
	});
	field_registry.add('tds_journal', ShowTdsJournalWidget);

});
