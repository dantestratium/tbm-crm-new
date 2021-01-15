odoo.define('crm_tbm_advanced.tour', function(require) {
"use strict";

var core = require('web.core');
var tour = require('web_tour.tour');

var _t = core._t;

tour.register = function() {
        var args = Array.prototype.slice.call(arguments);
        var last_arg = args[args.length - 1];
        var name = args[0];
        if (this.tours[name]) {
            console.warn(_.str.sprintf("Tour %s is already defined", name));
            return;
        }
        var options = args.length === 2 ? {} : args[1];
        var steps = last_arg instanceof Array ? last_arg : [last_arg];
        var tour = {
            name: name,
            steps: steps,
            url: options.url,
            rainbowMan: options.rainbowMan === undefined ? true : !!options.rainbowMan,
            test: options.test,
            wait_for: options.wait_for || $.when(),
        };
        if (options.skip_enabled) {
            tour.skip_link = '<p><span class="o_skip_tour">' + _t('Skip') + '</span></p>';
            tour.skip_handler = function (tip) {
                this._deactivate_tip(tip);
                this._consume_tip(tip, name);
            };
        }
        this.tours[name] = tour;
    }

tour.register('tbm_crm_opportunity_tour', {
    skip_enabled: true,
    rainbowMan: false,
    }, [
        {
            trigger: ".o_tour_new_equip",
            content: _t("Click to <b>conduct</b> an equipment survey for this opportunity."),
            position: "right"
        },
        {
            trigger: "div[name='crm_equipment_survey_sr_ids'] div.table-responsive a[role='button']",
            content: _t("Click to <b>add</b> speedwell for this survey."),
            position: "right"
        },
        {
            trigger: ".o_tour_quote_calc",
            content: _t("Click to <b>view</b> the quote calculation based on the survey.</b>"),
            position: "right"
        },
        {
            trigger: ".o_tour_new_quote",
            extra_trigger: '.o_opportunity_form.o_form_readonly',
            content: _t("Click to <b>create a quotation</b>. Verify all the lead information are <b>correct</b> before proceeding with quotation."),
            position: "right"
        }
    ]
);

tour.register('tbm_crm_lead_tour', {
    skip_enabled: true,
    rainbowMan: false,
    }, [
        {
            trigger: ".leads_form input.o_field_char[name=partner_name]",
            extra_trigger: '.leads_form.o_form_editable',
            content: _t("Enter <b>establishment name</b>. This will be used as the parent company of the contact."),
            position: "right"
        },
        {
            trigger: ".leads_form input.o_field_email[name=email_from]",
            extra_trigger: '.leads_form.o_form_editable',
            content: _t("Enter <b>email address</b>. The email will be used throughout the CRM system. e.g. sending of SO."),
            position: "left"
        },
        {
            trigger: ".leads_form input.o_field_phone[name=phone]",
            extra_trigger: '.leads_form.o_form_editable',
            content: _t("Enter <b>phone number</b>. Phonecalls can be logged within the system for future preferences."),
            position: "left"
        },
        {
            trigger: ".leads_form div.o_field_many2one[name=source_id]",
            extra_trigger: '.leads_form.o_form_editable',
            content: _t("Source information can be used to <b>categorize or group leads</b> in leads menu."),
            position: "right"
        },
        {
            trigger: ".leads_form button.o_chatter_button_schedule_activity",
            extra_trigger: '.leads_form.o_form_readonly',
            content: _t("Click to <b>Schedule an activity</b> for this lead. Activities includes email follow ups or meetings."),
            position: "top"
        },
        {
            trigger: ".leads_form button[data-value='warm']",
            extra_trigger: '.leads_form.o_form_readonly',
            content: _t("Click to <b>change lead classification</b>. Classifications separates the new leads from the processed ones."),
            position: "bottom"
        },
        {
            trigger: ".leads_form button[help='Convert to Opportunity']",
            extra_trigger: '.leads_form.o_form_readonly',
            content: _t("Click to <b>convert the lead</b> to opportunity. Establishment and contact will be saved as partners and allows the processing of Equipment Survey."),
            position: "right"
        },
    ]
);

tour.register('tbm_crm_sales_tour', {
    skip_enabled: true,
    rainbowMan: false,
    }, [
        {
            trigger: ".o_sale_order li.nav-item:nth-child(2)",
            content: _t("Click to see <b>optional products</b> available. e.g. extended warranty, extended license agreement."),
            position: "top"
        },
        {
            trigger: ".o_sale_order li.nav-item:nth-child(4)",
            content: _t("Click to see <b>estimated payments</b> of quotation and its payment breakdown."),
            position: "top"
        },
        {
            trigger: ".o_sale_order button[name='action_quotation_send']",
            content: _t("Click to <b>compose</b> an email for quotation and send to customer."),
            position: "right"
        },
        {
            trigger: "aside.o_cp_sidebar > div.btn-group > div:nth-child(2)",
            content: _t("Click to <b>Attachments</b> to add and upload documents provided by the customer. e.g. Financial and bank statements, tax returns."),
            position: "left"
        },
        {
            trigger: ".o_sale_order button[name='1094']",
            content: _t("Click to <b>create</b> loan application for customer."),
            position: "right"
        },
        {
            trigger: ".o_sale_order li.nav-item:nth-child(3)",
            content: _t("Click to see <b>submitted or processed</b> loan applications."),
            position: "top"
        },
        {
            trigger: "button[name='action_approve']",
            content: _t("Click to <b>approve</b> selected vendor for the current quotation."),
            position: "right"
        },
        {
            trigger: ".o_sale_order button[name='action_confirm']",
            content: _t("Click to <b>confirm</b> the quotation and convert it to Sales Order."),
            position: "right"
        },
    ]
);

tour.register('tbm_crm_delivery_tour', {
    skip_enabled: true,
    rainbowMan: false,
    }, [
        {
            trigger: ".o_sale_order li.nav-item:nth-child(2)",
            content: _t("Click to see <b>optional products</b> available. e.g. extended warranty, extended license agreement."),
            position: "top"
        }
    ]
);

});
