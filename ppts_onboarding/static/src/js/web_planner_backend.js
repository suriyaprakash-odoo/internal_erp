odoo.define('ppts_onboarding', function (require) {
	"use strict";
	var core = require('web.core');
	var SystrayMenu = require('web.SystrayMenu');
	var Widget = require('web.Widget');
	var QWeb = core.qweb;
	var rpc = require('web.rpc');
	var web_client = require('web.web_client');
	var utils = require('web.utils');
	
	var GetStarted = Widget.extend ({
		init: function() {
			var arg1=$(".form_id").text();		
		    var self = this;
		    rpc.query({
	            model: 'hr.employee.onboarding',
	            method: 'get_started_info',       
	            args: [[1], arg1],

	        }).then(function(get_started_dict){
	        	setTimeout(function(){
					if(get_started_dict){
						$(".smart_buttons_list").each(function(){
							$(this).find("button").eq(0).find("span.o_form_field_number").text(parseFloat(get_started_dict.score).toFixed(2));
						});
						if(get_started_dict.priority == 0){
							$('.good').attr("class","o_priority_star fa fa-star-o priority_very_good good");
							$('.very_good').attr("class","o_priority_star fa fa-star-o priority_very_good very_good");
							$('.excellent').attr("class",'o_priority_star fa fa-star-o priority_excellent excellent');
							$('.good').attr("style","color: #666666 !important;");
							$('.very_good').attr("style","color: #666666 !important;");
							$('.excellent').attr("style","color: #666666 !important;");
						}
						if(get_started_dict.priority == 1){
							$('.very_good').attr("class","o_priority_star fa fa-star-o priority_very_good very_good");
							$('.excellent').attr("class",'o_priority_star fa fa-star-o priority_excellent excellent');
							$('.very_good').attr("style","color: #666666 !important;");
							$('.excellent').attr("style","color: #666666 !important;");
						}
						if(get_started_dict.priority == 2){
							$('.excellent').attr("class",'o_priority_star fa fa-star-o priority_excellent excellent');
							$('.excellent').attr("style","color: #666666 !important;");
						}
						$(".form_name").html(get_started_dict.name);
						$(".form_phone").html(get_started_dict.phone);
						$(".form_email").html(get_started_dict.mail);
						$(".form_applied_job").html(get_started_dict.applied_job);
						$(".form_applicant_id").html(get_started_dict.applicant_id);
						$(".form_company").html(get_started_dict.company);
						$(".form_responsible").html(get_started_dict.responsible);
						$(".form_expected_salary").html(get_started_dict.expected_salary);
						$(".form_proposed_salary").html(get_started_dict.proposed_salary);
						$(".form_availability").html(get_started_dict.available);
						$(".form_pay_type").val(get_started_dict.pay_type);
						
						$(".form_contract_type").html("<option value=''></option>");
						$.each(get_started_dict.contract_type_disp, function(key,val) {
							$(".form_contract_type").append("<option value='"+key+"'>"+val+"</option>");
						});
						$(".form_contract_type").val(get_started_dict.contract_type);
						var name = get_started_dict.name
						$(".emp_name").text(get_started_dict.name+' has been Successfully Onboarded.');
						
					}

					$(".top_section").html("");
					$(".top_section").html($(".top_section_main").html());
				},500);
			});
	   }
});	
	
var InsertValsGetStarted = Widget.extend ({
		init: function() {
			var arg1=$(".form_id").text();
			var get_started = {con_typ:$(".form_contract_type").val(), pay_typ:$(".form_pay_type").val()};
			rpc.query({
	            model: 'hr.employee.onboarding',
	            method: 'insert_records_get_started',       
	            args: [[1], arg1,get_started],

	        }).then(function(result_vals){	
	        	$(".o_next_step").click();
				if(result_vals=='started'){
					alert('Please send the PID document');
				}
				else{
					$(".btn-next").click();
				}
			});
		}
});

var PersonalInfo = Widget.extend ({
	init: function() {
		var arg1=$(".form_id").text();
		rpc.query({
            model: 'hr.employee.onboarding',
            method: 'personalinfo',       
            args: [[1], arg1],
        }).then(function(personal_info_dict) {
				if(personal_info_dict){
					$(".form_pob").val(personal_info_dict.place_of_birth);
					$(".form_id_no").val(personal_info_dict.id_no);
					$(".form_passport_no").val(personal_info_dict.passport_no);
					$(".form_driving_license_no").val(personal_info_dict.dl_no);
					$(".form_street").val(personal_info_dict.street);
					$(".form_street2").val(personal_info_dict.street2);
					$(".form_city").val(personal_info_dict.city);
					

					$(".form_state").html("<option value=''></option>");
					
					$.each(personal_info_dict.state_dict, function(key,val) {
						$(".form_state").append("<option value='"+key+"'>"+val+"</option>");
					});
					$(".form_state").val(personal_info_dict.state);

					$(".form_zip").val(personal_info_dict.zip);
					$(".form_first_name_alias").val(personal_info_dict.first_name_alias);
					$(".form_middle_name_alias").val(personal_info_dict.middle_name_alias);
					$(".form_last_name_alias").val(personal_info_dict.last_name_alias);
					$(".form_gender").val(personal_info_dict.gender);
					$(".form_marital_status").val(personal_info_dict.marital_status);
					$(".form_children").val(personal_info_dict.children);
					$(".form_ethnic_id").val(personal_info_dict.ethnic_id);
					$(".form_smoker").val(personal_info_dict.smoker);
					$(".form_dob").val(personal_info_dict.dob);
					$(".form_age").val(personal_info_dict.age);
					$(".form_emergency_name").val(personal_info_dict.emergency_contact_name);
					$(".form_relationship").val(personal_info_dict.emergency_contact_relationship);
					$(".form_emergency_phone").val(personal_info_dict.emergency_contact_phone);

					$(".form_birth_country").html("<option value=''></option>");
					$(".form_country").html("<option value=''></option>");
					$(".form_nationality").html("<option value=''></option>");
					$.each(personal_info_dict.country, function(key,val) {
						$(".form_country").append("<option value='"+key+"'>"+val+"</option>");
						$(".form_nationality").append("<option value='"+key+"'>"+val+"</option>");
						$(".form_birth_country").append("<option value='"+key+"'>"+val+"</option>");
						
					});
					$(".form_country").val(personal_info_dict.country_id);
					$(".form_nationality").val(personal_info_dict.nationality);
					$(".form_birth_country").val(personal_info_dict.birth_country);
				}
		});
   }
});

var InsertValsPersonalInfo = Widget.extend ({
	init: function() {
		var arg1=$(".form_id").text();
		var personal_info = {
				id_no:$(".form_id_no").val(), 
				passport_no:$(".form_passport_no").val(),
				dl_no:$(".form_driving_license_no").val(),
				street:$(".form_street").val(),
				street2:$(".form_street2").val(),
				city:$(".form_city").val(),
				state:$(".form_state").val(),
				country:$(".form_country").val(),
				zip:$(".form_zip").val(),
				fst_name_alias:$(".form_first_name_alias").val(),
				mid_name_alias:$(".form_middle_name_alias").val(),
				lst_name_alias:$(".form_last_name_alias").val(),
				emergency_contact_name:$(".form_emergency_name").val(),
				emergency_contact_relationship:$(".form_relationship").val(),
				emergency_contact_phone:$(".form_emergency_phone").val(),
				gender:$(".form_gender").val(),
				nationality:$(".form_nationality").val(),
				birth_country:$(".form_birth_country").val(),
				marital_sts:$(".form_marital_status").val(),
				noc:$(".form_children").val(),
				ethnic:$(".form_ethnic_id").val(),
				smoker:$(".form_smoker").val(),
				dob:$(".form_dob").val(),
				age:$(".form_age").val(),
				place_of_birth:$(".form_pob").val(),
				image:$(".image_value").val()

			};
		rpc.query({
            model: 'hr.employee.onboarding',
            method: 'insert_records_personal_info',       
            args: [[1], arg1,personal_info],
        }).then(function(result_vals){
// if(result_vals == 'experience'){
// $(".o_next_step").click();
// }
// else{
// }
		});
   }
});

var ExperienceInfo = Widget.extend ({
	init: function() {

		var arg1=$(".form_id").text();
		rpc.query({
            model: 'hr.employee.onboarding',
            method: 'experienceinfo',       
            args: [[1], arg1],
        }).then(function(experience_info_dict){
				if(experience_info_dict){
					$.each(experience_info_dict, function(key,val) {
						if(key=='state_dict') {
							$.each(experience_info_dict['state_dict'], function(keys,vals) {
								$(".form_certification_exp_state_issued").append("<option value='"+keys+"'>"+vals+"</option>");
							});
						}
					});
					$.each(experience_info_dict, function(key_main,exp_val) { 
					
					if(key_main=='exp_academic_list'){		
						var i=0;
							$.each(exp_val, function(key,aca_val) {
								if(i==0){
									$(".form_academic_exp_tree_id").val(aca_val['form_academic_exp_tree_id']);
									$(".form_academic_exp").val(aca_val['academic_experience']);
									$(".form_academic_institution").val(aca_val['institute']);
									$(".form_academic_fos").val(aca_val['field_of_study']);
									$(".form_academic_year_passing").val(aca_val['year_of_passing']);
									$(".form_academic_percentage").val(aca_val['percentage']);
									i++;
								}else{
									if(i==1){
										$(".academic_exp_offer_accepted tbody").find("tr:gt(1)").remove();
// $(".form_academic_exp_tree_id").val(aca_val['form_academic_exp_tree_id']);
// $(".form_academic_exp").val(aca_val['academic_experience']);
// $(".form_academic_institution").val(aca_val['institute']);
// $(".form_academic_fos").val(aca_val['field_of_study']);
// $(".form_academic_year_passing").val(aca_val['year_of_passing']);
// $(".form_academic_percentage").val(aca_val['percentage']);
									}
// else {
									$(".academic_exp_offer_accepted tbody").append("<tr class='inc"+i+"'>"+$(".academic_exp_offer_accepted tr").eq(1).html()+"</tr>");
									
									$(".inc"+i+" .form_academic_exp_tree_id").val(aca_val['form_academic_exp_tree_id']);								
									$(".inc"+i+" .form_academic_exp").val(aca_val['academic_experience']);
									$(".inc"+i+" .form_academic_institution").val(aca_val['institute']);
									$(".inc"+i+" .form_academic_fos").val(aca_val['field_of_study']);
									$(".inc"+i+" .form_academic_year_passing").val(aca_val['year_of_passing']);
									$(".inc"+i+" .form_academic_percentage").val(aca_val['percentage']);
// }
									i++;
								}
							});									
						}
					if(key_main=='exp_professional_list'){
					  var i=0;
						$.each(exp_val, function(key,pro_val) {
							if(i==0){
								$(".form_professional_exp_tree_id").val(pro_val['form_professional_exp_tree_id']);
								$(".form_professional_exp_position").val(pro_val['position']);
								$(".form_professional_exp_organization").val(pro_val['organization']);
								$(".form_professional_exp_start_date").val(pro_val['start_date']);
								$(".form_professional_exp_end_date").val(pro_val['end_date']);
								i++;
							}else{
								if(i==1){
									$(".professional_exp_offer_accepted tbody").find("tr:gt(1)").remove();
// $(".form_professional_exp_tree_id").val(pro_val['form_professional_exp_tree_id']);
// $(".form_professional_exp_position").val(pro_val['position']);
// $(".form_professional_exp_organization").val(pro_val['organization']);
// $(".form_professional_exp_start_date").val(pro_val['start_date']);
// $(".form_professional_exp_end_date").val(pro_val['end_date']);
								}
// else{
								$(".professional_exp_offer_accepted tbody").append("<tr class='inc"+i+"'>"+$(".professional_exp_offer_accepted tr").eq(1).html()+"</tr>");
								$(".inc"+i+" .form_professional_exp_tree_id").val(pro_val['form_professional_exp_tree_id']);											
								$(".inc"+i+" .form_professional_exp_position").val(pro_val['position']);
								$(".inc"+i+" .form_professional_exp_employer").val(pro_val['employer']);
								$(".inc"+i+" .form_professional_exp_start_date").val(pro_val['start_date']);
								$(".inc"+i+" .form_professional_exp_end_date").val(pro_val['end_date']);
								i++;
// }
								
							}
						});
						
						}
					if(key_main=='exp_certificate_list'){
						var i=0;
						$.each(exp_val, function(key,aca_val) {
							if(i==0){
								$(".form_certification_exp_tree_id").val(aca_val['form_certification_exp_tree_id']);
								$(".form_certification_exp_certificate").val(aca_val['certifications']);
								$(".form_certification_exp_certificate_code").val(aca_val['certificate_code']);
								$(".form_certification_exp_issued_by").val(aca_val['issued_by']);
// if (aca_val['professional_license'] == true){
// $(".form_certification_exp_professional_license").attr('checked','checked');
// }
								$(".form_certification_exp_state_issued").val(aca_val['state_issued_id']);
								$(".form_certification_exp_start_date").val(aca_val['start_date']);
								$(".form_certification_exp_end_date").val(aca_val['end_date']);
								i++;
							}else{
								if(i==1){
									$(".certification_exp_offer_accepted tbody").find("tr:gt(1)").remove();
// $(".form_certification_exp_tree_id").val(aca_val['form_certification_exp_tree_id']);
// $(".form_certification_exp_certificate").val(aca_val['certifications']);
// $(".form_certification_exp_certificate_code").val(aca_val['certificate_code']);
// $(".form_certification_exp_issued_by").val(aca_val['issued_by']);
// // if (aca_val['professional_license'] == true){
// //
// $(".form_certification_exp_professional_license").attr('checked','checked');
// // }
// $(".form_certification_exp_state_issued").val(aca_val['state_issued_id']);
// $(".form_certification_exp_start_date").val(aca_val['start_date']);
// $(".form_certification_exp_end_date").val(aca_val['end_date']);
								}
								
								else {
									
									$(".certification_exp_offer_accepted tbody").append("<tr class='inc"+i+"'>"+$(".certification_exp_offer_accepted tr").eq(1).html()+"</tr>");
									$(".inc"+i+" .form_certification_exp_tree_id").val(aca_val['form_certification_exp_tree_id']);											
									$(".inc"+i+" .form_certification_exp_certificate").val(aca_val['certifications']);
									$(".inc"+i+" .form_certification_exp_certificate_code").val(aca_val['certificate_code']);
									$(".inc"+i+" .form_certification_exp_issued_by").val(aca_val['issued_by']);
// if (aca_val['professional_license'] == true){
// $(".inc"+i+"
// .form_certification_exp_professional_license").attr('checked','checked');
// }
									$(".inc"+i+" .form_certification_exp_state_issued").val(aca_val['state_issued_id']);
									$(".inc"+i+" .form_certification_exp_start_date").val(aca_val['start_date']);
									$(".inc"+i+" .form_certification_exp_end_date").val(aca_val['end_date']);
									i++;
								}
								
							}
						});
						
						}
							
			        });   
					
				}else{

				}
		});
   }
});

var InsertValsExpirenceInfo = Widget.extend ({
	init: function() {
		var arg1=$(".form_id").text();
		var n=0;
		$('.academic_exp_offer_accepted tr').each(function(){
			if(n>=1){
				var offer_accepted_academic_info = {
					academic_tree_id:$(this).find('.form_academic_exp_tree_id').val(), 
					academic_exp:$(this).find('.form_academic_exp').val(),
					academic_institution:$(this).find('.form_academic_institution').val(),
					academic_fos:$(this).find('.form_academic_fos').val(),
					academic_passing:$(this).find('.form_academic_year_passing').val(),
					academic_percentage:$(this).find('.form_academic_percentage').val(),
				};
				rpc.query({
		            model: 'hr.employee.onboarding',
		            method: 'insert_records_experience_academic_info',       
		            args: [[1], arg1,offer_accepted_academic_info],
		        }).then(function(){
				});
			}
			n++;
		});
		var m=0;
		$('.professional_exp_offer_accepted tr').each(function(){
			if(m>=1){
				var offer_accepted_professional_info = {
					professional_tree_id:$(this).find('.form_professional_exp_tree_id').val(), 
					position:$(this).find('.form_professional_exp_position').val(),
					organization:$(this).find('.form_professional_exp_organization').val(),
					professional_start:$(this).find('.form_professional_exp_start_date').val(),
					professional_end:$(this).find('.form_professional_exp_end_date').val(),
				};
				rpc.query({
		            model: 'hr.employee.onboarding',
		            method: 'insert_records_experience_professional_info',       
		            args: [[1], arg1,offer_accepted_professional_info],
		        }).then(function(){
				});
			}
			m++;
		});
		var p=0;
		$('.certification_exp_offer_accepted tr').each(function(){
			if(p>=1){
				var professional_license_val = ''
				if($(this).find('.form_certification_exp_professional_license').is(':checked')){
					professional_license_val = true
				}
				var offer_accepted_certificate_info = {
					certificate_tree_id:$(this).find('.form_certification_exp_tree_id').val(), 
					certificate:$(this).find('.form_certification_exp_certificate').val(),
					certificate_no:$(this).find('.form_certification_exp_certificate_code').val(),
					issued_by:$(this).find('.form_certification_exp_issued_by').val(),
					professional_license:professional_license_val,
					state_issued_id:$(this).find('.form_certification_exp_state_issued').val(),
					certificate_start:$(this).find('.form_certification_exp_start_date').val(),
					certificate_end:$(this).find('.form_certification_exp_end_date').val(),
				};
				rpc.query({
		            model: 'hr.employee.onboarding',
		            method: 'insert_records_experience_certification_info',       
		            args: [[1], arg1,offer_accepted_certificate_info],
		        }).then(function(result_vals){
		        	if(result_vals == 'medical'){
						$(".o_next_step").click();
					}
					else{
					}
				});
			}
			p++;
		});
   }
}); 

var MedicalInformation = Widget.extend ({
	init: function() {
		var arg1=$(".form_id").text();
		rpc.query({
            model: 'hr.employee.onboarding',
            method: 'medicalinformation',       
            args: [[1], arg1],
        }).then(function(medical_information_dict) {
// $(".form_job_seniority_title").html("<option value=''></option>");
				if(medical_information_dict){
					$(".form_vision").val(medical_information_dict.vision);
					$(".form_chronic").val(medical_information_dict.chronic);
					$(".form_undergone").val(medical_information_dict.undergone);
					$(".form_cardiac").val(medical_information_dict.cardiac);
					$(".form_frequent").val(medical_information_dict.frequent);
					$(".form_any_other").val(medical_information_dict.others);
				}
		});
   }
});

var InsertValsMedicalInfo = Widget.extend ({
	init: function() {
		var arg1=$(".form_id").text();
		var medical_info = {
				vision:$(".form_vision").val(), 
				chronic:$(".form_chronic").val(),
				undergone:$(".form_undergone").val(),
				cardiac:$(".form_cardiac").val(),
				frequent:$(".form_frequent").val(),
				other:$(".form_any_other").val(),
				
			};
		rpc.query({
            model: 'hr.employee.onboarding',
            method: 'insert_records_medical_info',       
            args: [[1], arg1,medical_info],
        }).then(function(result_vals){
			if(result_vals == 'experience'){
				$(".o_next_step").click();
			}
			else{
			}
		});
   }
});

var EmployementInfo = Widget.extend ({
	init: function() {
		var arg1=$(".form_id").text();
		rpc.query({
            model: 'hr.employee.onboarding',
            method: 'employementinfo',       
            args: [[1], arg1],
        }).then(function(employement_info_dict){
        	$(".form_job_seniority_title").html("<option value=''></option>");
        	$.each(employement_info_dict.seniority, function(job_key,job_val) {
				$(".form_job_seniority_title").append("<option value='"+job_key+"'>"+job_val+"</option>");
			});	
			if(employement_info_dict){
				$(".form_contract_type").val(employement_info_dict.contract_type)
				$(".form_start_date").val(employement_info_dict.emp_start_date);					
				$(".form_benefits_seniority_date").val(employement_info_dict.benifits_seniority_date);

// $(".form_job_seniority_title").html("<option value=''></option>");
// $.each(employement_info_dict.job_seniority_title_disp,
// function(job_key,job_val) {
// $(".form_job_seniority_title").append("<option
// value='"+job_key+"'>"+job_val+"</option>");
// });
				$(".form_job_seniority_title").val(employement_info_dict.job_seniority_title);

			}
		});
   }
});

var InsertValsEmployementInfo = Widget.extend ({
	init: async function() {
		var arg1=$(".form_id").text();
		var employement_info = {
			job_seniority_title:$(".form_job_seniority_title").val(), 
			start_date:$(".form_start_date").val(),
			benefits_seniority_date:$(".form_benefits_seniority_date").val(),
			seniority:$(".form_job_seniority_title").val(),
		};
		let promise = new Promise((resolve, reject) => {});
			// setTimeout(function(){
// var hr_onboarding = new Model('hr.employee.onboarding');
// hr_onboarding.call('insert_records_employement_info', [[1],
// arg1,employement_info])
// .then(function(result_vals)
			rpc.query({
            model: 'hr.employee.onboarding',
            method: 'insert_records_employement_info',       
            args: [[1], arg1,employement_info],
        }).then(function(result_vals){
// resolve(result_vals);
				});
			// },10000);
		
		let result = await promise;
		if(result){
			$(".o_next_step").click();
		}
   	}
});






// # Thanos


var onboadinginfo = Widget.extend ({
	init: function() {
		var arg1=$(".form_id").text();			
	    var self = this;
	    rpc.query({
            model: 'hr.employee.onboarding',
            method: 'onboadinginfo',       
            args: [[1], arg1],
        }).then(function(onboadinginfo_dict){
        	
				if(onboadinginfo_dict){
					if(onboadinginfo_dict.board_nda == 'eligible'){
						$(".on_nda").attr('checked','checked');
					}
					if(onboadinginfo_dict.board_employeestatus == 'eligible'){
						$(".on_employeemanual").attr('checked','checked');
					}
				}
		});
   }
});

var Insertonboadinginfo = Widget.extend ({
	init: function() {
		var arg1=$(".form_id").text();
		if($('input.on_nda').is(':checked')){
			var benefits_nda = 'checked'
		}
		if($('input.on_employeemanual').is(':checked')){
			var benefits_employeemanual = 'checked'
		}
		 rpc.query({
	            model: 'hr.employee.onboarding',
	            method: 'insert_onboadinginfo',       
	            args: [[1], arg1,benefits_nda,benefits_employeemanual],
	        }).then(function(){
		});
   }
});


var OfferSummary = Widget.extend ({
	init: function() {
		var arg1=$(".form_id").text();			
	    var self = this;
	    rpc.query({
            model: 'hr.employee.onboarding',
            method: 'offer_summary',       
            args: [[1], arg1],
        }).then(function(offer_summary_dict){
				if(offer_summary_dict){
					$(".form_summary_name").val(offer_summary_dict.name);
					$(".form_summary_phone").val(offer_summary_dict.phone);
					$(".form_summary_mail").val(offer_summary_dict.mail);
					$(".form_summary_applied_job").val(offer_summary_dict.applied_job);
					$(".form_summary_applicant_id").val(offer_summary_dict.applicant_id);
					$(".form_summary_company").val(offer_summary_dict.company);
					$(".form_summary_responsible").val(offer_summary_dict.responsible);
					$(".form_summary_id_number").val(offer_summary_dict.id_no);
					$(".form_summary_passport_number").val(offer_summary_dict.passport_no);
					$(".form_street").val(offer_summary_dict.street);
					$(".form_street2").val(offer_summary_dict.street2);
					$(".form_city").val(offer_summary_dict.city);
					$(".form_summary_state").val(offer_summary_dict.state);
					$(".form_summary_country").val(offer_summary_dict.country_id);
					$(".form_zip").val(offer_summary_dict.zip);
					$(".form_summary_gender").val(offer_summary_dict.gender);
					$(".form_summary_marital_status").val(offer_summary_dict.marital_status);
// $(".form_summary_noc").val(offer_summary_dict.children);
					$(".form_summary_dob").val(offer_summary_dict.dob);
					$(".form_summary_age").val(offer_summary_dict.age);
					$(".form_summary_scheduled_hours").val(offer_summary_dict.scheduled_hours);
					$(".form_summary_pay_rate").val(offer_summary_dict.pay_rate);
					$(".form_summary_start_date").val(offer_summary_dict.emp_start_date);		
					$(".form_job_seniority_title").val(offer_summary_dict.job_seniority_title);
					$(".form_summary_ben_sen_date").val(offer_summary_dict.benifits_seniority_date);
					$(".form_summary_country").val(offer_summary_dict.nationality);
					$(".form_summary_nationality").val(offer_summary_dict.nationality);
					$(".form_summary_birth_country").val(offer_summary_dict.birth_country);	

					$(".form_summary_employment_status").html("<option value=''></option>");
					$.each(offer_summary_dict.emp_sts_disp, function(job_key,job_val) {
						$(".form_summary_employment_status").append("<option value='"+job_key+"'>"+job_val+"</option>");
					});	
					$(".form_summary_employment_status").val(offer_summary_dict.emp_status);

					$(".form_summary_pob").val(offer_summary_dict.place_of_birth);
					$.each(offer_summary_dict, function(key_main,exp_val) { 
						if(key_main=='exp_academic_list'){		
							var i=0;
								$.each(exp_val, function(key,aca_val) {
									if(i==0){
										$(".form_academic_exp_tree_id").val(aca_val['academic_tree_id']);
										$(".form_academic_exp").val(aca_val['degree']);
										$(".form_academic_institution").val(aca_val['institute']);
										$(".form_academic_fos").val(aca_val['field_of_study']);
										$(".form_academic_year_passing").val(aca_val['year_of_passing']);
										$(".form_academic_percentage").val(aca_val['percentage']);
										i++;
									}else{
										if(i==1){
											$(".academic_exp_offer_accepted_summary tbody").find("tr:gt(1)").remove();
										}
										$(".academic_exp_offer_accepted_summary tbody").append("<tr class='inc"+i+"'>"+$(".academic_exp_offer_accepted_summary tr").eq(1).html()+"</tr>");
										
										$(".inc"+i+" .form_academic_exp_tree_id").val(aca_val['academic_tree_id']);								
										$(".inc"+i+" .form_academic_exp").val(aca_val['degree']);
										$(".inc"+i+" .form_academic_institution").val(aca_val['institute']);
										$(".inc"+i+" .form_academic_fos").val(aca_val['field_of_study']);
										$(".inc"+i+" .form_academic_year_passing").val(aca_val['year_of_passing']);
										$(".inc"+i+" .form_academic_percentage").val(aca_val['percentage']);
										i++;
									}
								});									
							}
						if(key_main=='exp_professional_list'){

							var i=0;
							$.each(exp_val, function(key,pro_val) {
								if(i==0){
									$(".form_professional_exp_tree_id").val(pro_val['professional_tree_id']);
									$(".form_professional_exp_position").val(pro_val['position']);
									$(".form_professional_exp_organization").val(pro_val['organization']);
									$(".form_professional_exp_start_date").val(pro_val['start_date']);
									$(".form_professional_exp_end_date").val(pro_val['end_date']);
									i++;
								}else{
									if(i==1){
										$(".professional_exp_offer_accepted_summary tbody").find("tr:gt(1)").remove();
									}
									$(".professional_exp_offer_accepted_summary tbody").append("<tr class='inc"+i+"'>"+$(".professional_exp_offer_accepted_summary tr").eq(1).html()+"</tr>");
									$(".inc"+i+" .form_professional_exp_tree_id").val(pro_val['professional_tree_id']);											
									$(".inc"+i+" .form_professional_exp_position").val(pro_val['position']);
									$(".inc"+i+" .form_professional_exp_employer").val(pro_val['employer']);
									$(".inc"+i+" .form_professional_exp_start_date").val(pro_val['start_date']);
									$(".inc"+i+" .form_professional_exp_end_date").val(pro_val['end_date']);
									i++;
								}
							});
							
							}
						if(key_main=='exp_certificate_list'){
							var i=0;
							$.each(exp_val, function(key,aca_val) {
								if(i==0){
									$(".form_certification_exp_tree_id").val(aca_val['certification_tree_id']);
									$(".form_certification_exp_certificate").val(aca_val['certifications']);
									$(".form_certification_exp_certificate_code").val(aca_val['certificate_code']);
									$(".form_certification_exp_issued_by").val(aca_val['issued_by']);
									if (aca_val['professional_license'] == true){
										$(".form_certification_exp_professional_license").attr('checked','checked');
									}
									$(".form_certification_exp_state_issued").val(aca_val['state_issued_id']);
									$(".form_certification_exp_start_date").val(aca_val['start_date']);
									$(".form_certification_exp_end_date").val(aca_val['end_date']);
									i++;
								}else{
									if(i==1){
										$(".certification_exp_offer_accepted_summary tbody").find("tr:gt(1)").remove();
									}
									$(".certification_exp_offer_accepted_summary tbody").append("<tr class='inc"+i+"'>"+$(".certification_exp_offer_accepted_summary tr").eq(1).html()+"</tr>");
									$(".inc"+i+" .form_certification_exp_tree_id").val(aca_val['certification_tree_id']);											
									$(".inc"+i+" .form_certification_exp_certificate").val(aca_val['certifications']);
									$(".inc"+i+" .form_certification_exp_certificate_code").val(aca_val['certificate_code']);
									$(".inc"+i+" .form_certification_exp_issued_by").val(aca_val['issued_by']);
									if (aca_val['professional_license'] == true){
										$(".inc"+i+" .form_certification_exp_professional_license").attr('checked','checked');
									}
									$(".inc"+i+" .form_certification_exp_state_issued").val(aca_val['state_issued_id']);
									$(".inc"+i+" .form_certification_exp_start_date").val(aca_val['start_date']);
									$(".inc"+i+" .form_certification_exp_end_date").val(aca_val['end_date']);
									i++;
								}
							});
							
							}
						
		        });   
				}
		});
   }
});

var InsertValsOfferSummary= Widget.extend ({
	init: function() {
		var arg1=$(".form_id").text();
		var summary_info = {
				summary_employment_status:$(".form_summary_employment_status").val(), 
				summary_scheduled_hours:$(".form_summary_scheduled_hours").val(), 
				summary_pay_rate:$(".form_summary_pay_rate").val(),
				};
		rpc.query({
            model: 'hr.employee.onboarding',
            method: 'summary_state',       
            args: [[1], arg1,summary_info],
        }).then(function(){
		});
   }
});

$(document).on('focus',".date_time_picker_custom", function(){
	 $(this).datetimepicker({
		 
		 format: 'YYYY-MM-DD hh:mm:ss'
		 
	 });
	
});

var BackgroundInfo = Widget.extend ({
	init: function() {
		var arg1=$(".form_id").text();
		rpc.query({
            model: 'hr.employee.onboarding',
            method: 'bgv_info',       
            args: [[1], arg1],
        }).then(function(bgv_info_dict){
			$.each(bgv_info_dict, function(key_main,val_main) { 
				if(key_main=='bgv_list'){		
					var i=0;
						$.each(val_main, function(bgv_key,bgv_val) {
							if(i==0){
								$(".form_bgv_tree_id").val(bgv_val['tree_id']);
								$(".form_bgv_name").val(bgv_val['name']);
								$(".form_bgv_mail").val(bgv_val['mail']);
								$(".form_bgv_contact_no").val(bgv_val['contact']);
								i++;
							}else{
								if(i==1){
									$(".bgv_details_table tbody").find("tr:gt(1)").remove();
								}
								$(".bgv_details_table tbody").append("<tr class='inc"+i+"'>"+$(".bgv_details_table tr").eq(1).html()+"</tr>");
								
								$(".inc"+i+" .form_bgv_tree_id").val(bgv_val['tree_id']);
								$(".inc"+i+" .form_bgv_name").val(bgv_val['name']);
								$(".inc"+i+" .form_bgv_mail").val(bgv_val['mail']);
								$(".inc"+i+" .form_bgv_contact_no").val(bgv_val['contact']);
								i++;
							}
						});									
					}
				});   
			});
		}
});

var InsertValsBackgroundVerification = Widget.extend ({
	init: function() {
		var arg1=$(".form_id").text();
		var n=0;
		$('.bgv_details_table tr').each(function(){
			if(n>=1){
				var bgv_info_vals = {
						form_bgv_tree_id:$(this).find('.form_bgv_tree_id').val(), 
						form_bgv_name:$(this).find('.form_bgv_name').val(),
						form_bgv_mail:$(this).find('.form_bgv_mail').val(),
						form_bgv_contact_no:$(this).find('.form_bgv_contact_no').val(),
					};
			    rpc.query({
	            model: 'hr.employee.onboarding',
	            method: 'insert_records_bgv_info',       
	            args: [[1], arg1,bgv_info_vals],
	        }).then(function(){
				});
			}
			n++;
		});
		
		// var substate_name = 'inine';
		// var state_name = 'to_approve';
	 //    var hr_onboarding_state = new Model('hr.employee.onboarding');
		// hr_onboarding_state.call('change_status', [[1], arg1,substate_name,state_name])
		// .then(function() {
		// });
   }
});

var BackgroundCheck = Widget.extend ({
	
	init: function() {
		var arg1=$(".form_id").text();
		rpc.query({
            model: 'hr.employee.onboarding',
            method: 'backgroundinfo',       
            args: [[1], arg1],
        }).then(function(background_info_dict) {
				if(background_info_dict){
					$(".form_background_tenure").val(background_info_dict.tenure);
					$(".form_background_cost_company").val(background_info_dict.cost_of_comapny);
					$(".form_background_manage_name").val(background_info_dict.reporting_manger_name);
					$(".form_background_manage_designation").val(background_info_dict.reporting_manger_designation);
					$(".form_background_reason_leaving").val(background_info_dict.reason_leaving);
					$(".form_background_attached_document").val(background_info_dict.attached_document);
					$(".form_background_feedback_on_account").val(background_info_dict.feedback_on_account);
					$(".form_background_source_of_verification").val(background_info_dict.source_of_verification);
					$(".form_background_exit_formalities").val(background_info_dict.exit_formalities);
					$(".form_background_designation").val(background_info_dict.designation);
					$(".form_background_employee_code").val(background_info_dict.employee_code);
					$(".form_background_manage_email_id").val(background_info_dict.reporting_manger_email_id);
					$(".form_background_manager_tele_no").val(background_info_dict.reporting_manger_tele_no);
					$(".form_background_eligibility_for_rehire").val(background_info_dict.eligibility_for_rehire);
					$(".form_background_referee_details").val(background_info_dict.referee_details);
					$(".form_background_date_and_time").val(background_info_dict.date_and_time);
					$(".form_background_notice_period").val(background_info_dict.notice_period);
					$(".form_background_any_other_commands").val(background_info_dict.any_other_commands);
					
				}
		});
   }
});

var InsertValsBackgroundCheck = Widget.extend ({
	init: function() {
		var arg1=$(".form_id").text();
		var background_check_info = {
				background_tenure:$(".form_background_tenure").val(), 
				background_cost_of_comapny:$(".form_background_cost_company").val(), 
				background_reporting_manger_name:$(".form_background_manage_name").val(),
				background_reporting_manger_designation:$(".form_background_manage_designation").val(),
				background_reason_leaving:$(".form_background_reason_leaving").val(),
				background_attached_document:$(".form_background_attached_document").val(),
				background_feedback_on_account:$(".form_background_feedback_on_account").val(),
				background_source_of_verification:$(".form_background_source_of_verification").val(),
				background_exit_formalities:$(".form_background_exit_formalities").val(),
				background_designation:$(".form_background_designation").val(),
				background_employee_code:$(".form_background_employee_code").val(),
				background_reporting_manger_email_id:$(".form_background_manage_email_id").val(),
				background_reporting_manger_tele_no:$(".form_background_manager_tele_no").val(),
				background_eligibility_for_rehire:$(".form_background_eligibility_for_rehire").val(),
				background_referee_details:$(".form_background_referee_details").val(),
				background_date_and_time:$(".form_background_date_and_time").val(),
				background_notice_period:$(".form_background_notice_period").val(),
				background_any_other_commands:$(".form_background_any_other_commands").val(),
				};
		rpc.query({
            model: 'hr.employee.onboarding',
            method: 'insert_records_backgroundinfo',       
            args: [[1], arg1,background_check_info],
        }).then(function(){
		});
   }
});

var SummaryBackgroundCheck = Widget.extend ({
	init: function() {
		var arg1=$(".form_id").text();
		rpc.query({
            model: 'hr.employee.onboarding',
            method: 'summarybackgroundinfo',       
            args: [[1], arg1],
        }).then(function(summary_background_info_dict) {
				if(summary_background_info_dict){
					$(".form_summary_background_tenure").val(summary_background_info_dict.tenure);
					$(".form_summary_background_cost_company").val(summary_background_info_dict.cost_of_comapny);
					$(".form_summary_background_manage_name").val(summary_background_info_dict.reporting_manger_name);
					$(".form_summary_background_manage_designation").val(summary_background_info_dict.reporting_manger_designation);
					$(".form_summary_background_reason_leaving").val(summary_background_info_dict.reason_leaving);
					$(".form_summary_background_attached_document").val(summary_background_info_dict.attached_document);
					$(".form_summary_background_feedback_on_account").val(summary_background_info_dict.feedback_on_account);
					$(".form_summary_background_source_of_verification").val(summary_background_info_dict.source_of_verification);
					$(".form_summary_background_exit_formalities").val(summary_background_info_dict.exit_formalities);
					$(".form_summary_background_designation").val(summary_background_info_dict.designation);
					$(".form_summary_background_employee_code").val(summary_background_info_dict.employee_code);
					$(".form_summary_background_manage_email_id").val(summary_background_info_dict.reporting_manger_email_id);
					$(".form_summary_background_manager_tele_no").val(summary_background_info_dict.reporting_manger_tele_no);
					$(".form_summary_background_eligibility_for_rehire").val(summary_background_info_dict.eligibility_for_rehire);
					$(".form_summary_background_referee_details").val(summary_background_info_dict.referee_details);
					$(".form_summary_background_date_and_time").val(summary_background_info_dict.date_and_time);
					$(".form_summary_background_notice_period").val(summary_background_info_dict.notice_period);
					$(".form_summary_background_any_other_commands").val(summary_background_info_dict.any_other_commands);
					$(".form_aadhar_card").val(summary_background_info_dict.aadhar_card);
		        	$(".form_voter_id").val(summary_background_info_dict.voter_id);
		        	$(".form_tenth_marksheet").val(summary_background_info_dict.tenth_marksheet);
		        	$(".form_twelveth_marksheet").val(summary_background_info_dict.twelveth_marksheet);
		        	$(".form_college_marksheet").val(summary_background_info_dict.college_marksheet);
		        	$(".form_tc").val(summary_background_info_dict.tc);
					
				}
		});
   }
});

var InsertRecordSummaryBackgroundCheck = Widget.extend ({
	init: function() {
		var arg1=$(".form_id").text();
		var background_check_info = {
				};
		rpc.query({
            model: 'hr.employee.onboarding',
            method: 'insert_record_summarybackgroundinfo',       
            args: [[1], arg1],
        }).then(function(){
		});
   }
});

var HireSummary = Widget.extend ({
	init: function() {
		var arg1=$(".form_id").text();			
	    var self = this;
// var hr_onboarding = new Model('hr.employee.onboarding');
// hr_onboarding.call('offer_summary', [[1], arg1])
// .then(function(offer_summary_dict)
	    rpc.query({
            model: 'hr.employee.onboarding',
            method: 'hire_summary',       
            args: [[1], arg1],
        }).then(function(hire_summary_dict){
				if(hire_summary_dict){
					$(".form_summary_name").val(hire_summary_dict.name);
					$(".form_summary_phone").val(hire_summary_dict.phone);
					$(".form_summary_mail").val(hire_summary_dict.mail);
					$(".form_summary_applied_job").val(hire_summary_dict.applied_job);
					$(".form_summary_applicant_id").val(hire_summary_dict.applicant_id);
					$(".form_summary_company").val(hire_summary_dict.company);
					$(".form_summary_responsible").val(hire_summary_dict.responsible);
					$(".form_summary_id_number").val(hire_summary_dict.id_no);
					$(".form_summary_passport_number").val(hire_summary_dict.passport_no);
					$(".form_street").val(hire_summary_dict.street);
					$(".form_street2").val(hire_summary_dict.street2);
					$(".form_city").val(hire_summary_dict.city);
					$(".form_summary_state").val(hire_summary_dict.state);
					$(".form_summary_country").val(hire_summary_dict.country_id);
					$(".form_zip").val(hire_summary_dict.zip);
					$(".form_summary_gender").val(hire_summary_dict.gender);
					$(".form_summary_marital_status").val(hire_summary_dict.marital_status);
// $(".form_summary_noc").val(hire_summary_dict.children);
					$(".form_summary_dob").val(hire_summary_dict.dob);
					$(".form_summary_age").val(hire_summary_dict.age);
					$(".form_summary_scheduled_hours").val(hire_summary_dict.scheduled_hours);
					$(".form_summary_pay_rate").val(hire_summary_dict.pay_rate);
					$(".form_summary_start_date").val(hire_summary_dict.emp_start_date);		
					$(".form_job_seniority_title").val(hire_summary_dict.job_seniority_title);
					$(".form_summary_ben_sen_date").val(hire_summary_dict.benifits_seniority_date);
					$(".form_summary_country").val(hire_summary_dict.nationality);
					$(".form_summary_nationality").val(hire_summary_dict.nationality);
					$(".form_summary_birth_country").val(hire_summary_dict.birth_country);	

// $(".form_summary_employment_status").html("<option value=''></option>");
// $.each(hire_summary_dict.state_dict, function(job_key,job_val) {
// $(".form_summary_employment_status").append("<option
// value='"+job_key+"'>"+job_val+"</option>");
// });
					$(".form_summary_employment_status").val(hire_summary_dict.emp_status);

					$(".form_summary_pob").val(hire_summary_dict.place_of_birth);
					$.each(hire_summary_dict, function(key_main,exp_val) { 
						if(key_main=='exp_academic_list'){		
							var i=0;
								$.each(exp_val, function(key,aca_val) {
									if(i==0){
										$(".form_academic_exp_tree_id").val(aca_val['academic_tree_id']);
										$(".form_academic_exp").val(aca_val['degree']);
										$(".form_academic_institution").val(aca_val['institute']);
										$(".form_academic_fos").val(aca_val['field_of_study']);
										$(".form_academic_year_passing").val(aca_val['year_of_passing']);
										$(".form_academic_percentage").val(aca_val['percentage']);
										i++;
									}else{
										if(i==1){
											$(".academic_exp_offer_accepted_summary tbody").find("tr:gt(1)").remove();
										}
										$(".academic_exp_offer_accepted_summary tbody").append("<tr class='inc"+i+"'>"+$(".academic_exp_offer_accepted_summary tr").eq(1).html()+"</tr>");
										
										$(".inc"+i+" .form_academic_exp_tree_id").val(aca_val['academic_tree_id']);								
										$(".inc"+i+" .form_academic_exp").val(aca_val['degree']);
										$(".inc"+i+" .form_academic_institution").val(aca_val['institute']);
										$(".inc"+i+" .form_academic_fos").val(aca_val['field_of_study']);
										$(".inc"+i+" .form_academic_year_passing").val(aca_val['year_of_passing']);
										$(".inc"+i+" .form_academic_percentage").val(aca_val['percentage']);
										i++;
									}
								});									
							}
						if(key_main=='exp_professional_list'){

							var i=0;
							$.each(exp_val, function(key,pro_val) {
								if(i==0){
									$(".form_professional_exp_tree_id").val(pro_val['professional_tree_id']);
									$(".form_professional_exp_position").val(pro_val['position']);
									$(".form_professional_exp_organization").val(pro_val['organization']);
									$(".form_professional_exp_start_date").val(pro_val['start_date']);
									$(".form_professional_exp_end_date").val(pro_val['end_date']);
									i++;
								}else{
									if(i==1){
										$(".professional_exp_offer_accepted_summary tbody").find("tr:gt(1)").remove();
									}
									$(".professional_exp_offer_accepted_summary tbody").append("<tr class='inc"+i+"'>"+$(".professional_exp_offer_accepted_summary tr").eq(1).html()+"</tr>");
									$(".inc"+i+" .form_professional_exp_tree_id").val(pro_val['professional_tree_id']);											
									$(".inc"+i+" .form_professional_exp_position").val(pro_val['position']);
									$(".inc"+i+" .form_professional_exp_employer").val(pro_val['employer']);
									$(".inc"+i+" .form_professional_exp_start_date").val(pro_val['start_date']);
									$(".inc"+i+" .form_professional_exp_end_date").val(pro_val['end_date']);
									i++;
								}
							});
							
							}
						if(key_main=='exp_certificate_list'){
							var i=0;
							$.each(exp_val, function(key,aca_val) {
								if(i==0){
									$(".form_certification_exp_tree_id").val(aca_val['certification_tree_id']);
									$(".form_certification_exp_certificate").val(aca_val['certifications']);
									$(".form_certification_exp_certificate_code").val(aca_val['certificate_code']);
									$(".form_certification_exp_issued_by").val(aca_val['issued_by']);
									if (aca_val['professional_license'] == true){
										$(".form_certification_exp_professional_license").attr('checked','checked');
									}
									$(".form_certification_exp_state_issued").val(aca_val['state_issued_id']);
									$(".form_certification_exp_start_date").val(aca_val['start_date']);
									$(".form_certification_exp_end_date").val(aca_val['end_date']);
									i++;
								}else{
									if(i==1){
										$(".certification_exp_offer_accepted_summary tbody").find("tr:gt(1)").remove();
									}
									$(".certification_exp_offer_accepted_summary tbody").append("<tr class='inc"+i+"'>"+$(".certification_exp_offer_accepted_summary tr").eq(1).html()+"</tr>");
									$(".inc"+i+" .form_certification_exp_tree_id").val(aca_val['certification_tree_id']);											
									$(".inc"+i+" .form_certification_exp_certificate").val(aca_val['certifications']);
									$(".inc"+i+" .form_certification_exp_certificate_code").val(aca_val['certificate_code']);
									$(".inc"+i+" .form_certification_exp_issued_by").val(aca_val['issued_by']);
									if (aca_val['professional_license'] == true){
										$(".inc"+i+" .form_certification_exp_professional_license").attr('checked','checked');
									}
									$(".inc"+i+" .form_certification_exp_state_issued").val(aca_val['state_issued_id']);
									$(".inc"+i+" .form_certification_exp_start_date").val(aca_val['start_date']);
									$(".inc"+i+" .form_certification_exp_end_date").val(aca_val['end_date']);
									i++;
								}
							});
							
							}
						
		        });   
				}
		});
   }
});

$(document).ready(function(){


function calculateAge (birthDate, otherDate) {
    birthDate = new Date(birthDate);
    otherDate = new Date(otherDate);

    var years = (otherDate.getFullYear() - birthDate.getFullYear());

    if (otherDate.getMonth() < birthDate.getMonth() || 
        otherDate.getMonth() == birthDate.getMonth() && otherDate.getDate() < birthDate.getDate()) {
        years--;
    }

    return years;
}
$(document).delegate('.form_dob','change',function() {
    $('.form_age').val(calculateAge($(this).val(),new Date()));
});
});



var ChangeState = Widget.extend ({
	init: function() {
		var country_id=$(".form_country").val();
// var hr_onboarding = new Model('hr.employee.onboarding');
// hr_onboarding.call('change_state_name', [[1],
// country_id]).then(function(state_dict)
		
		 rpc.query({
	            model: 'hr.employee.onboarding',
	            method: 'change_state_name',       
	            args: [[1], country_id],
	        }).then(function(state_dict){
			if(state_dict){
				var old_val=$(".form_state").val();
				$(".form_state").html("<option value=''></option>");
				$.each(state_dict, function(key,val) {
					$(".form_state").append("<option value='"+key+"'>"+val+"</option>");
				});
				$(".form_state").val(old_val);
			}				
		});
   }
});


$(document).delegate('.form_country','change',function() {
    new ChangeState();
});


var CreateEmployee = Widget.extend ({
	init: function() {
		var arg1=$(".form_id").text();			
	    var self = this;
	    rpc.query({
            model: 'hr.employee.onboarding',
            method: 'create_employee',       
            args: [[1], arg1],
        }).then(function(){
        	
        });
        }
});

var BenefitsEligibility = Widget.extend ({
	init: function() {
		var arg1=$(".form_id").text();			
	    var self = this;
	    rpc.query({
            model: 'hr.employee.onboarding',
            method: 'benefits_eligibility_info',       
            args: [[1], arg1],
        }).then(function(benefits_eligibility_dict){
        	
				if(benefits_eligibility_dict){
					if(benefits_eligibility_dict.ben_eligible_epf == 'eligible'){
						$(".benefits_epf").attr('checked','checked');
						$("#formpf").show();
					}
					if(benefits_eligibility_dict.ben_eligible_esi == 'eligible'){
						$(".benefits_esi").attr('checked','checked');
						$("#formesino").show();
					}
					if(benefits_eligibility_dict.ben_eligible_medical_policy == 'eligible'){
						$(".benefits_medical_policy").attr('checked','checked');
					}
					$(".form_summary_aadhaar").val(benefits_eligibility_dict.aadhaar);
					$(".form_summary_pan").val(benefits_eligibility_dict.pan);
					$(".form_summary_pf").val(benefits_eligibility_dict.pf);
					$(".form_summary_esino").val(benefits_eligibility_dict.esino);
				}
		});
   }
});

var InsrtValsBenefitsEligibility = Widget.extend ({
	init: function() {
		var arg1=$(".form_id").text();
		if($('input.benefits_epf').is(':checked')){
			var benefits_epf = 'checked'
		}
		if($('input.benefits_esi').is(':checked')){
			var benefits_esi = 'checked'
		}
		if($('input.benefits_medical_policy').is(':checked')){
			var benefits_medical_policy = 'checked'
		}
// var hr_onboarding = new Model('hr.employee.onboarding');
// hr_onboarding.call('insert_vals_benefits_eligibility', [[1], arg1,ban_obj])
// .then(function()
		var benefits_eligibility_info = {
				summary_aadhaar:$(".form_summary_aadhaar").val(), 
				summary_pan:$(".form_summary_pan").val(),
				summary_pf:$(".form_summary_pf").val(),
				summary_esino:$(".form_summary_esino").val(),
				};
		 rpc.query({
	            model: 'hr.employee.onboarding',
	            method: 'insert_vals_benefits_eligibility',       
	            args: [[1], arg1,benefits_epf,benefits_esi,benefits_medical_policy,benefits_eligibility_info],
	        }).then(function(){
		});
   }
});

var AppraisalInfo = Widget.extend ({
	init: function() {
		var arg1=$(".form_id").text();
		rpc.query({
            model: 'hr.employee.onboarding',
            method: 'appraisal_info',       
            args: [[1], arg1],
        }).then(function(appraisal_info_dict){
				if(appraisal_info_dict){
					if(appraisal_info_dict.appraisal_by_manager == 1){
						$(".apprasial_manager").attr('checked','checked');
					}
					if(appraisal_info_dict.appraisal_self == 1){
						$(".apprasial_employee").attr('checked','checked');
					}
					if(appraisal_info_dict.appraisal_by_tl == 1){
						$(".apprasial_tl").attr('checked','checked');
					}
					if(appraisal_info_dict.appraisal_by_ro == 1){
						$(".apprasial_ro").attr('checked','checked');
					}
					if(appraisal_info_dict.appraisal_by_hr == 1){
						$(".apprasial_hr").attr('checked','checked');
					}
					if(appraisal_info_dict.periodic_appraisal == 1){
						$(".periodic_appraisal").attr('checked','checked');
					}
					$(".repeat_period").val(appraisal_info_dict.appraisal_frequency);
					$(".period").val(appraisal_info_dict.appraisal_frequency_unit);
					$(".next_appraisal_date").val(appraisal_info_dict.appraisal_date);
				}
		});
   }
});

var InsertValsAppraisalInfo = Widget.extend ({
	init: function() {
		var arg1=$(".form_id").text();
		var days_appraisal='';
		/*
		 * if($('input.apprasial_employee').is(':checked')){
		 * days_appraisal=$(".apprasial_employee").val(); }
		 */
		var manager='';
		if($('input.apprasial_manager').is(':checked')){
			manager=$(".apprasial_manager").val();
		}
		var employee='';
		if($('input.apprasial_employee').is(':checked')){
			employee=$(".apprasial_employee").val();
		}
		var tl='';
		if($('input.apprasial_tl').is(':checked')){
			tl=$(".apprasial_tl").val();
		}
		var ro='';
		if($('input.apprasial_ro').is(':checked')){
			ro=$(".apprasial_ro").val();
		}
		var hr='';
		if($('input.apprasial_hr').is(':checked')){
			hr=$(".apprasial_hr	").val();
		}
		var periodic_appraisal='';
		if($('input.periodic_appraisal').is(':checked')){
			periodic_appraisal=$(".periodic_appraisal").val();
		}
		var appraisal_plan_info = {	
				apprasial_manager : manager,
				employee : employee,
				tl : tl,
				ro : ro,
				hr : hr,
				periodic_appraisal : periodic_appraisal,
				repeat_period : $(".repeat_period").val(), 
				period : $(".period").val(),
				next_appraisal_date : $(".next_appraisal_date").val(),
			};
		rpc.query({
            model: 'hr.employee.onboarding',
            method: 'insert_records_appraisal_info',       
            args: [[1], arg1,appraisal_plan_info],
        }).then(function(){
		});
   }
});

var WelcomeMail = Widget.extend ({
	init: function() {
		var arg1=$(".form_id").text();
		rpc.query({
            model: 'hr.employee.onboarding',
            method: 'welcome_mail',       
            args: [[1], arg1],
        }).then(function(welcome_mail_id){
        	if(welcome_mail_id){
        		$(".form_website_mail_template").val(welcome_mail_id);
        	}
        });
        }
});		

var SendWelcomeMail = Widget.extend ({
	init: function() {
		var arg1=$(".form_id").text();
		rpc.query({
            model: 'hr.employee.onboarding',
            method: 'send_welcome_email',       
            args: [[1], arg1,],
        }).then(function(){
        });
        }
});		

var DocumentCheck = Widget.extend ({
	init: function() {
		var arg1=$(".form_id").text();
		rpc.query({
            model: 'hr.employee.onboarding',
            method: 'document_check',       
            args: [[1], arg1,],
        }).then(function(document_check_dict){
        	$(".form_aadhar_card").val(document_check_dict.aadhar_card);
        	$(".form_voter_id").val(document_check_dict.voter_id);
        	$(".form_tenth_marksheet").val(document_check_dict.tenth_marksheet);
        	$(".form_twelveth_marksheet").val(document_check_dict.twelveth_marksheet);
        	$(".form_college_marksheet").val(document_check_dict.college_marksheet);
        	$(".form_tc").val(document_check_dict.tc);
        	
        });
        }
});	

var InsertDocumentCheck = Widget.extend ({
	init: function() {
		var arg1=$(".form_id").text();
		var document_check_info = {
				aadhar_card:$(".form_aadhar_card").val(), 
				voter_id:$(".form_voter_id").val(), 
				tenth_marksheet:$(".form_tenth_marksheet").val(),
				twelveth_marksheet:$(".form_twelveth_marksheet").val(),
				college_marksheet:$(".form_college_marksheet").val(),
				tc:$(".form_tc").val(),
				};
		rpc.query({
            model: 'hr.employee.onboarding',
            method: 'insert_document_check',       
            args: [[1], arg1,document_check_info],
        }).then(function(){
        	
        });
        }
});	

var EmployeeInfo = Widget.extend ({
	init: function() {
		var arg1=$(".form_id").text();			
	    var self = this;
		// var hr_onboarding = new Model('hr.employee.onboarding');
		// hr_onboarding.call('employee_info', [[1], arg1])
		// .then(function(employee_info_dict)
		rpc.query({
        	model: 'hr.employee.onboarding',
        	method: 'employee_info',       
        	args: [[1], arg1],
    	}).then(function(employee_info_dict){
			if(employee_info_dict){
				$(".form_employee_summary_name").val(employee_info_dict.name);
				$(".work_address").val(employee_info_dict.address_id);
				$(".work_street2").val(employee_info_dict.street2);
				$(".work_city").val(employee_info_dict.city);
				$(".work_state").val(employee_info_dict.state);
				$(".work_country").val(employee_info_dict.country);
				$(".work_mobile").val(employee_info_dict.mobile_phone);
				$(".work_email").val(employee_info_dict.work_email);
				$(".work_phone").val(employee_info_dict.work_phone);
				$(".primary_job").val(employee_info_dict.job_id);
				$(".job_seniority_title").val(employee_info_dict.job_seniority_title);
				$(".contract_type").val(employee_info_dict.contract_type);
				$(".manager").val(employee_info_dict.parent_id);
				$(".coach").val(employee_info_dict.coach_id);
				$(".department").val(employee_info_dict.department_id);
				$(".working_hours").val(employee_info_dict.resource_calendar_id);
				if(employee_info_dict.manager_checkbox == 1){
					$(".is_a_manager").attr('checked','checked');
				}
				$(".nationality").val(employee_info_dict.country_id);
				$(".identification_no").val(employee_info_dict.identification_id);
				$(".passport_no").val(employee_info_dict.passport_id);
				$(".home_address").val(employee_info_dict.address_home_id);
				$(".gender").val(employee_info_dict.gender);
				$(".marital_status").val(employee_info_dict.marital);
				$(".no_of_child").val(employee_info_dict.children);
				$(".date_of_birth").val(employee_info_dict.birthday);
				$(".place_of_birth").val(employee_info_dict.place_of_birth);
				$(".birth_country").val(employee_info_dict.birth_country);
				$(".age").val(employee_info_dict.age);
				$(".visa_number").val(employee_info_dict.visa_no);
				$(".permit_number").val(employee_info_dict.permit_no);
				$(".visa_expiration").val(employee_info_dict.visa_expire);
				$(".timesheet_cost").val(employee_info_dict.timesheet_cost);
				$(".related_user").val(employee_info_dict.user_id);
				$(".hire_date").val(employee_info_dict.hire_date);
				$(".medical_exam").val(employee_info_dict.medic_exam);
				$(".company_vehicel").val(employee_info_dict.vehicle);
				$(".home_work_dist").val(employee_info_dict.vehicle_distance);
				$(".rem_legal_leave").val(employee_info_dict.remaining_leaves);
				if(employee_info_dict.appraisal_self == 1){
					$(".employee").attr('checked','checked');
				}
				if(employee_info_dict.appraisal_by_tl == 1){
					$(".team_lead").attr('checked','checked');
				}
				if(employee_info_dict.appraisal_by_ro == 1){
					$(".report_officer").attr('checked','checked');
				}
				if(employee_info_dict.appraisal_by_manager == 1){
					$(".manager").attr('checked','checked');
				}
				if(employee_info_dict.appraisal_by_hr == 1){
					$(".human_resources").attr('checked','checked');
				}
				if(employee_info_dict.periodic_appraisal == 1){
					$(".periodic_appraisal").attr('checked','checked');
				}
				$(".next_appraisal_date").val(employee_info_dict.appraisal_date);
			}
		});
   }
});

var ContractInfo = Widget.extend ({
	init: function() {	
		var arg1=$(".form_id").text();			
	    var self = this;
		// var hr_onboarding = new Model('hr.employee.onboarding');
		// hr_onboarding.call('contract_info', [[1], arg1])
		// .then(function(contract_info_dict)
		rpc.query({
            model: 'hr.employee.onboarding',
            method: 'contract_info',       
            args: [[1], arg1],
        }).then(function(contract_info_dict){
			if(contract_info_dict){
				$(".contract_name").val(contract_info_dict.name);
				$(".form_employee_name").val(contract_info_dict.employee_id);
				$(".contract_form_contract_type").val(contract_info_dict.type_id);
				$(".form_primary_job").val(contract_info_dict.job_id);
				$(".form_scheduled_pay").val(contract_info_dict.schedule_pay);
				$(".form_working_schedule").val(contract_info_dict.working_schedule);
				$(".contract_form_job_sen_title").val(contract_info_dict.job_seniority_title);
				$(".form_trial_start").val(contract_info_dict.trial_date_start);
				$(".form_trial_end").val(contract_info_dict.trial_date_end);
				$(".form_duration_start").val(contract_info_dict.date_start);			
				$(".form_duration_end").val(contract_info_dict.date_end);			
				$(".form_notes").val(contract_info_dict.notes);
				$(".contract_form_department").val(contract_info_dict.department_id);
				$(".contract_form_wage").val(contract_info_dict.wage);			
				$(".contract_form_salary_structure").val(contract_info_dict.struct_id);

			}
		});
   }
});

var CreateContract = Widget.extend ({
init: function() {
	var arg1=$(".form_id").text();
	// var hr_onboarding = new Model('hr.employee.onboarding');
	// hr_onboarding.call('create_contract_via_link', [[1], arg1])
	// .then(function(res)
	rpc.query({
            model: 'hr.employee.onboarding',
            method: 'create_contract_via_link',       
            args: [[1], arg1],
        }).then(function(res){
		if(res){
			window.open($(".create_contract_link_redirect").attr("test")+"&id="+res,'_blank');
		}else{

		}				
	});
}
});

var Contract = Widget.extend ({
	init: function() {
		var arg1=$(".form_id").text();			
	    var self = this;
	    rpc.query({
            model: 'hr.employee.onboarding',
            method: 'contract',       
            args: [[1], arg1],
        }).then(function(){
        	
        });
        }
});


var Complete = Widget.extend ({
init: function() {
	var arg1=$(".form_id").text();
	// var hr_onboarding = new Model('hr.employee.onboarding');
	// hr_onboarding.call('create_contract_via_link', [[1], arg1])
	// .then(function(res)
	rpc.query({
            model: 'hr.employee.onboarding',
            method: 'complete',       
            args: [[1], arg1],
        }).then(function(res){
// new Complete();
		
	});
}
});

// Var Complete = Widget.extend ({
// init: function() {
// var arg1=$(".form_id").text();
// //var hr_onboarding = new Model('hr.employee.onboarding');
// //hr_onboarding.call('create_contract_via_link', [[1], arg1])
// //.then(function(res)
// // rpc.query({
// // model: 'hr.employee.onboarding',
// // method: 'create_contract_via_link',
// // args: [[1], arg1],
// // }).then(function(res){
// // if(res){
// //
// window.open($(".create_contract_link_redirect").attr("test")+"&id="+res,'_blank');
// // }else{
// //
// // }
// // });
// }
// });

$(document).delegate('.create_contract_link_redirect','click',function() {
		new CreateContract();
	});

$(document).delegate('.btn_sent.btn_bgv_send','click',function() {

			var parent_val=$(this).parent();
			var arg1 = $(".form_id").text();	
			var doc_id = {
				form_bgv_tree_id:$(this).parent().find('.form_bgv_tree_id').val(), 
				form_bgv_name:$(this).parent().find('.form_bgv_name').val(),
				form_bgv_mail:$(this).parent().find('.form_bgv_mail').val(),
				form_bgv_contact_no:$(this).parent().find('.form_bgv_contact_no').val(),
			}
			var tree_id = $(this).parent().find('.form_bgv_tree_id').val();
			rpc.query({
            model: 'hr.employee.onboarding',
            method: 'send_bgv_survey',       
            args: [[1], arg1,tree_id,doc_id],
        }).then(function(res){
				
			});			
		});

// # Wakanda forever
$(document).delegate('.benefits_epf','click',function() {
if($('#pf_checked:checked').val()){
	   $("#formpf").show();
	 }
	 else{
	   $("#formpf").hide();
	   }
});

$(document).delegate('.benefits_esi','click',function() {
if($('#esi_checked:checked').val()){
	   $("#formesino").show();
	 }
	 else{
	   $("#formesino").hide();
	   }
});


var encodeImageFileAsURL = Widget.extend ({
	init: function() {

    var filesSelected = document.getElementById("inputFileToLoad").files;
      	if (filesSelected.length > 0) {
	        var fileToLoad = filesSelected[0];

	        var fileReader = new FileReader();

	        fileReader.onload = function(fileLoadedEvent) {
	        var srcData = fileLoadedEvent.target.result; // <--- data: base64

	        var newImage = document.createElement('img');
	        newImage.src = srcData;

	        newImage.style="height:150px;"

	        document.getElementById("imgTest").innerHTML = newImage.outerHTML;
	        // alert("Converted Base64 version is " + document.getElementById("imgTest").innerHTML);
	        console.log( $("#imgTest img").attr("src"));
	        $(".image_value").val($("#imgTest img").attr("src"));
	        }
	        fileReader.readAsDataURL(fileToLoad);
      	}
    }
});
$(document).ready(function(){	
		$('body').delegate('#inputFileToLoad','change',function() {
			new encodeImageFileAsURL();

		});
});







// Added for View More Redirect
var EmployeeView = Widget.extend ({
	init: function() {
		var arg1=$(".form_id").text();
		var hr_onboarding = new Model('hr.employee.onboarding');
		hr_onboarding.call('employee_view', [[1], arg1]).then(function(res) {
			if(res){
				window.open($(".edit_employee_info_redirect").attr("test")+"&id="+res,'_blank');
			}else{

			}				
		});
 }
});

// Added for View More Redirect to Employee Form
$('document').delegate('.edit_employee_info_redirect','click',function() {
			new EmployeeView();
		});

// Table Row Deleting
		$(document).delegate('.custom_tab li','click',function() {
			var cls=$(this).attr('class');
			$(".tab-pane").removeClass('active');
			$("#"+cls).addClass('active');
		});

/*
 * $('focus',".datepicker_custom",function () {
 * $('#datetimepicker1').datetimepicker(); });
 */
		$(document).on('focus',".datepicker_custom", function(){
	        $(this).datepicker({
	          changeMonth: true,
	          changeYear: true,
	          yearRange: "1940:2100",
	          dateFormat: "yy-mm-dd"
	        });
	    });
		$(document).ready(function(){		
// Offer Accepted Experience
$(document).delegate('.add_more_academic','click',function() {
	$(".academic_exp_offer_accepted tbody").append('<tr>\
		<td style="display:none">\
			<input class="input_box form_academic_exp_tree_id" value="0" type="text">\
		</td>\
		<td>\
			<input class="input_box form_academic_exp" value="" type="text" placeholder="Academic Degree" style="border:none">\
		</td>\
		<td>\
		<input class="input_box form_academic_fos" value="" type="text" placeholder="Field of study" style="border:none">\
		</td>\
		<td>\
			<input class="input_box form_academic_institution" value="" type="text" placeholder="Institution" style="border:none">\
		</td>\
		<td>\
			<input class="input_box form_academic_percentage" value="" type="text" style="border:none">\
		</td>\
		<td>\
			<input class="input_box form_academic_year_passing " value="" type="text" style="border:none">\
		</td>\
		<td class="onboard_trash"><i class="fa fa-trash"></i></td>\
	</tr>');
	$(document).on('focus',".datepicker_custom", function(){
        $(this).datepicker({
          changeMonth: true,
          changeYear: true,
          yearRange: "1940:2100",
          dateFormat: "yy-mm-dd"
        });
    });
	$(".academic_exp_offer_accepted tbody").find("tr:last").find(".form_academic_exp_tree_id").val(0);
});
	
/*
 * $(document).delegate('.attach_document','click',function() {
 * $(".academic_exp_offer_accepted tbody").append('<tr>\
 * <td style="display:none">\ <input class="input_box
 * form_academic_exp_tree_id" value="0" type="text">\ </td>\ <td>\ <input
 * class="input_box form_academic_exp" value="" type="text"
 * placeholder="Academic Experiences" style="border:none">\ </td>\ <td>\
 * <input class="input_box form_academic_fos" value="" type="text"
 * placeholder="Field of study" style="border:none">\ </td>\ <td>\ <input
 * class="input_box form_academic_institution" value="" type="text"
 * placeholder="Institution" style="border:none">\ </td>\ <td>\ <input
 * class="input_box form_academic_percentage" value="" type="text"
 * style="border:none">\ </td>\ <td>\ <input class="input_box
 * form_academic_year_passing " value="" type="text" style="border:none">\ </td>\
 * <td class="onboard_trash"><i class="fa fa-trash"></i></td>\ </tr>');
 * $(".academic_exp_offer_accepted
 * tbody").find("tr:last").find(".form_academic_exp_tree_id").val(0); });
 * 
 * $(document).on('focus',".datepicker_custom", function(){ $(this).datepicker({
 * changeMonth: true, changeYear: true, yearRange: "1940:2100", dateFormat:
 * "yy-mm-dd", }); });
 */
$(document).delegate('.add_more_professional','click',function() {
	$(".professional_exp_offer_accepted tbody").append('<tr>\
		<td style= "display:none">\
			<input class="input_box form_professional_exp_tree_id"  value="0"  type="text"/>\
		</td>\
		<td>\
			<input class="input_box form_professional_exp_position"  value=""  type="text" placeholder="Position" style="border:none" />\
		</td>\
		<td>\
			<input class="input_box form_professional_exp_organization"  value=""  type="text" placeholder="Organization" style="border:none" />\
		</td>\
		<td>\
			<input class="input_box form_professional_exp_start_date datepicker_custom"  value=""  type="text" style="border:none" />\
		</td>\
		<td>\
			<input class="input_box form_professional_exp_end_date datepicker_custom"  value=""  type="text" style="border:none" />\
		</td>\
		<td class="onboard_trash"><i class="fa fa-trash"></i></td>\
	</tr>');
	$(document).on('focus',".datepicker_custom", function(){
        $(this).datepicker({
          changeMonth: true,
          changeYear: true,
          yearRange: "1940:2100",
          dateFormat: "yy-mm-dd"
        });
    });
	$(".professional_exp_offer_accepted tbody").find("tr:last").find(".professional_exp_offer_accepted").val(0);
});
$(document).delegate('.add_more_certification','click',function() {
	$(".certification_exp_offer_accepted tbody").append('<tr>\
		<td style= "display:none">\
			<input class="input_box form_certification_exp_tree_id"  value="0"  type="text"/>\
		</td>\
		<td>\
			<input class="input_box form_certification_exp_certificate"  value=""  type="text" placeholder="Certifications" style="border:none" />\
		</td>\
		<td>\
			<input class="input_box form_certification_exp_issued_by"  value=""  type="text" placeholder="Issued By" style="border:none" />\
		</td>\
		<td>\
			<select name="State Issued" class="form_certification_exp_state_issued ">\
			'+$(".certification_exp_offer_accepted tr").eq(1).find(".form_certification_exp_state_issued").html()+'\
			</select>\
		</td>\
		<td>\
			<input class="input_box form_certification_exp_start_date datepicker_custom"  value=""  type="text" style="border:none" />\
		</td>\
		<td>\
			<input class="input_box form_certification_exp_end_date datepicker_custom"  value=""  type="text" style="border:none" />\
		</td>\
		<td class="onboard_trash"><i class="fa fa-trash"></i></td>\
	</tr>');
	$(document).on('focus',".datepicker_custom", function(){
        $(this).datepicker({
          changeMonth: true,
          changeYear: true,
          yearRange: "1940:2100",
          dateFormat: "yy-mm-dd",
          timeFormat: "HH:MM"	  
        });
    });
	$(".certification_exp_offer_accepted tbody").find("tr:last").find(".certification_exp_offer_accepted").val(0);
});


	$(document).delegate('.smart_buttons button','click',function() {
		var arg1 = $(".form_id").text();	
// var hr_onboarding = new Model('hr.employee.onboarding');
		/*
		 * hr_onboarding.call('smart_buttons', [[1], arg1])
		 * .then(function(smart_button_dict) { if(smart_button_dict){
		 * window.open('web#view_type=form&model=hr.applicant&action=hr_recruitment.crm_case_categ0_act_job&menu_id=hr_recruitment.menu_crm_case_categ0_act_job'+"&id="+smart_button_dict.applicant_id,'_blank'); }
		 * });
		 */
		rpc.query({
            model: 'hr.employee.onboarding',
            method: 'smart_buttons',       
            args: [[1], arg1],
        }).then(function(smart_button_dict){
        	if(smart_button_dict){
				window.open('web#view_type=form&model=hr.applicant&action=hr_recruitment.crm_case_categ0_act_job&menu_id=hr_recruitment.menu_crm_case_categ0_act_job'+"&id="+smart_button_dict.applicant_id,'_blank');
        	}
		});
		
	});
	
	$(document).delegate('.btn_welcome_package','click',function() {

		var arg1 = $(".form_id").text();
		var get_started = {con_typ:$(".form_contract_type").val(), pay_typ:$(".form_pay_type").val()};	
		var check_id = 'launch'
		var i=0;
	    $(".get_started .required_cls").each(function(){
	        if($(this).val()=='' || ($(this).val() == null)){
	        	i++;
	        	$(this).attr("style","border-bottom: 2px solid #f00 !important;");
	        }else{			        	
	        	$(this).attr("style","border-bottom: 2px solid #616161 !important");
	        }
	    });
		
		if(i>0){
			alert("Please fill all required fields");
		}
		rpc.query({
            model: 'hr.employee.onboarding',
            method: 'send_launch_pack',       
            args: [[1], arg1,check_id,get_started],
        }).then(function(result_vals){
			if(parseInt(result_vals)!=0){
				alert("Personal Information Document has been sent Successfully");
			}else{
				alert("Personal Information document is already sent");
			}
		});			
	});

	$(document).delegate('.onboard_trash','click',function() {
		if($(this).parent().parent().find('tr').length>2){
	    	var r = confirm("Do you want to delete this record?");
// alert($(this).parents('.form_tree_id').val());
	    	$(this).parents('tr').remove();
// if($(this).parents('form_tree_id').find('.form_tree_id').val()== 0) {
// alert(65435135453);
// $(this).parents('tr').remove();
// }
	    	if (r == true) {	    		
				var arg1=$(".form_id").text();
				rpc.query({
		            model: 'hr.employee.onboarding',
		            method: 'remove_record',       
		            args: [[1], arg1,$(this).parent().find('.form_tree_id').val(),$(this).parent().find('.form_tree_id').attr('data-model')],
		        }).then(function(res){
// new ExperienceInfo();
				});
				
			}
		}
	});
	

	function load_records(page_id){
		setTimeout(function(){ 
			new GetStarted();
		
		if (page_id =='PersonalInformation1'){
			new PersonalInfo();
		}
		if (page_id =='ExperienceandCertification2'){
			new ExperienceInfo();
		}
		if (page_id =='MedicalInformation3'){	
			new MedicalInformation();
		}
		if (page_id =='EmploymentInformation4'){
			new EmployementInfo();
			}
		if (page_id =='Summary5'){
			new OfferSummary();			
		}
		if (page_id =='BackgroundVerification6'){
			new BackgroundInfo();	
			
		}
		if (page_id =='BackgroundCheck7'){
			new BackgroundCheck();	
			
		}
		if (page_id =='DocumentCheck8'){
			new DocumentCheck();
		}
		if (page_id =='Summary9'){
			new SummaryBackgroundCheck();
		}
		if (page_id =='ApplicantSummary/Hire10'){
			new HireSummary();
		}
		if (page_id =='BenefitsEligibility11'){
			new BenefitsEligibility();
		}
		if (page_id =='WelcomeEmail12'){
			new WelcomeMail();
		}
		if (page_id =='OnboardingChecklist13'){
			new onboadinginfo();
		}
		if (page_id =='AppraisalPlan14'){
			new AppraisalInfo();
		}
		if (page_id =='EmployeeSummary15'){
			new EmployeeInfo();
		}
		if (page_id =='CreateContract16'){
		}
		if (page_id =='ContractSummary17'){
			new ContractInfo();
		}
		if (page_id =='Complete18'){
			new Complete();
		}

		});
	}
	
	
	$(document).delegate('.o_planner_menu li','click', async function() {
		// sub_state($(this).find('a').attr('href').replace("#",""));
		var click_page_id=$(this).find('a').attr('href').replace("#","");
		  let promise = new Promise((resolve, reject) => {
			  var arg1=$(".form_id").text();
			/*
			 * var hr_onboarding = new Model('hr.employee.onboarding');
			 * hr_onboarding.call('get_sub_state_id', [[1], arg1])
			 * .then(function(result_vals) { resolve(result_vals); });
			 */
			  rpc.query({
		            model: 'hr.employee.onboarding',
		            method: 'get_sub_state_id',       
		            args: [[1], arg1],
		        }).then(function(result_vals){
		        	resolve(result_vals);
				});
				
		  });


		let result = await promise; // wait till the promise resolves (*)
		var current_page_id = result;
		load_records(click_page_id);
		if(click_page_id==current_page_id){
			$(".btn_onboarding_next,.onboard_trash").show();
		}else{
			$(".btn_onboarding_next,.onboard_trash").show();
		}

		  
	});
	
// $(document).delegate(function () {
// alert('000000');
// $('.progress').show();
// });
	
	var DashboardPlanner = Widget.extend({
	    template: 'PlannerLauncher',

	    events: {
	        'click .btn_completion_bar_new': 'on_planner_clicked',
	    },
	    init: function(parent, data){
	        this.data = data;
	        this.parent = parent;
	        this.planner_by_menu = {};
	        this._super.apply(this, arguments);
	    },

	    willStart: function () {
	        var self = this;
	        return this._rpc({
	                model: 'web.planner',
	                method: 'search_read',
	            })
	            .then(function(res) {
	                self.planners = res;
	                _.each(self.planners, function(planner) {
	                    self.planner_by_menu[planner.menu_id[0]] = planner;
	                    self.planner_by_menu[planner.menu_id[0]].data = $.parseJSON(planner.data) || {};
	                });
	                self.set_overall_progress();
	            });
	    },

	    update_planner_progress: function(){
	        this.set_overall_progress();
	        this.$('.btn_completion_bar_new').replaceWith(
	            QWeb.render("DashboardPlanner.PlannersList", {'planners': this.planners})
	        );
	    },

	    set_overall_progress: function(){
	        var self = this;
	        this.sort_planners_list();
	        var average = _.reduce(self.planners, function(memo, planner) {
	            return planner.progress + memo;
	        }, 0) / (self.planners.length || 1);
	        self.overall_progress = Math.floor(average);
	        self.$('.o_web_settings_dashboard_planner_overall_progress').text(self.overall_progress);
	    },

	    on_planner_clicked: function (e) {
	        var menu_id = $(e.currentTarget).attr('data-menu-id');
	        this.planner = this.planner_by_menu[menu_id];

	        this.dialog = new PlannerDialog(this, undefined, this.planner);
	        console.log(this.dialog);
	        this.dialog.on("planner_progress_changed", this, function(percent) {
	            this.planner.progress = percent;
	            this.update_planner_progress();
	        });
	        this.dialog.open();
	    },
	});

	
	$(document).delegate('.btn_completion_bar_new','click',function() {
		var page_id = $(".substate_value").text();
		$(".progress").click();

// load_records(page_id);
		setTimeout(function(){ 
// $(".progress").click();
			$(".o_next_step").hide();
			$("a[href='#"+page_id+"']").click();
// alert(page_id);
			new GetStarted();
		
		if (page_id =='PersonalInformation1'){
			setTimeout(function(){ 
			new PersonalInfo();
			},100);
		}
		if (page_id =='ExperienceandCertifications2'){
			setTimeout(function(){ 
			new ExperienceInfo();
			},100);
		}
		if (page_id =='MedicalInfomation3'){	
			setTimeout(function(){ 
			new MedicalInformation();
			},100);
		}
		if (page_id =='EmployementInformation4'){
			setTimeout(function(){ 
			new EmployementInfo();
			},100);
			}
		if (page_id =='Summary5'){
			new OfferSummary();			
			setTimeout(function(){ 
				new EmployementInfo();
			});
		}
		if (page_id =='BackgroundVerification6'){
			setTimeout(function(){
				new BackgroundInfo();	
			},100);
			
		}
		if (page_id =='BackgroundCheck7'){
			setTimeout(function(){
				new BackgroundCheck();	
			},100);
			
		}
		if (page_id =='DocumentCheck8'){
			setTimeout(function(){
			new DocumentCheck();			
			},100);
		}
		if (page_id =='Summary9'){
			setTimeout(function(){ 
			new SummaryBackgroundCheck();
			},100);
		}
		if (page_id =='ApplicantSummary/Hire10'){
			setTimeout(function(){ 		
			new HireSummary();
			},100);
		}
		if (page_id =='BenefitsEligibility11'){
			setTimeout(function(){ 
			new BenefitsEligibility();
			},100);
		}
		if (page_id =='WelcomeEmail12'){
			setTimeout(function(){ 
			new WelcomeMail();
			},100);
		}
		if (page_id =='OnboardingChecklist13'){
			setTimeout(function(){ 
			new onboadinginfo();
			},100);
		}
		if (page_id =='AppraisalPlan14'){
			setTimeout(function(){ 
			new AppraisalInfo();
			},100);
		}
		if (page_id =='EmployeeSummary15'){
			setTimeout(function(){ 
			new EmployeeInfo();
			},100);
		}
		if (page_id =='CreateContract16'){
			setTimeout(function(){ 
// new AppraisalInfo();
			},100);
		}
		if (page_id =='ContractSummary17'){
			setTimeout(function(){ 
				new ContractInfo();
			},100);
		}
		if (page_id =='Complete18'){
			setTimeout(function(){ 
			new Complete();
			},100);
		}

		},1000);
		
// $(".o_next_step").hide();
		
// load_records(page_id);
	});
	

		$(".modal-footer").hide();
		$(".top_section").html("");
		$(".top_section").appendTo($(".top_section_main").html());
	

	/*
	 * $('.modal-header .close').on('click',function(){ location.reload(); });
	 */
	
	$(document).delegate('.btn_onboarding_next','click',function() {
		if($(this).attr('data_page_id')=='1'){
			var i=0;
		    $(".get_started .required_cls").each(function(){
		        if($(this).val()=='' || ($(this).val() == null)){
		        	i++;
		        	$(this).attr("style","border-bottom: 2px solid #f00 !important;");
		        }else{			        	
		        	$(this).attr("style","border-bottom: 2px solid #616161 !important");
		        }
		    });
			
			if(i>0){
				alert("Please fill all required fields");
			}
			else{
				new InsertValsGetStarted();
				setTimeout(function(){ 
					new PersonalInfo();
// $(".o_next_step").click();
					$(".o_next_step").hide();
				},500);
			}
		}
		if($(this).attr('data_page_id')=='2'){
			var i=0;
		    $(".personal_info .required_cls").each(function(){
		        if($(this).val()=='' || ($(this).val() == null)){
		        	i++;
		        	$(this).attr("style","border-bottom: 2px solid #f00 !important;");
		        }else{			        	
		        	$(this).attr("style","border-bottom: 2px solid #616161 !important");
		        }
		    });
			
			if(i>0){
				alert("Please fill all required fields");
			}
			else{
				new InsertValsPersonalInfo();
				setTimeout(function(){ 
					new ExperienceInfo();
					$(".o_next_step").click();
					$(".o_next_step").hide();
				},500);
			}
		}
		if($(this).attr('data_page_id')=='3'){
			new InsertValsExpirenceInfo();
			setTimeout(function(){ 
				new MedicalInformation();	
// $(".o_next_step").click();
				$(".o_next_step").hide();
			},1000);
		}
		if($(this).attr('data_page_id')=='4'){
			var i=0;
		    $(".medical_info .required_cls").each(function(){
		        if($(this).val()=='' || ($(this).val() == null)){
		        	i++;
		        	$(this).attr("style","border-bottom: 2px solid #f00 !important;");
		        }else{			        	
		        	$(this).attr("style","border-bottom: 2px solid #616161 !important");
		        }
		    });
			
			if(i>0){
				alert("Please fill all required fields");
			}
			else{
				new InsertValsMedicalInfo();
				setTimeout(function(){ 
					new EmployementInfo();
					 $(".o_next_step").click();
					$(".o_next_step").hide();
				},500);
			}
		}
		if($(this).attr('data_page_id')=='5'){
			var i=0;
		    $(".employement_info .required_cls").each(function(){
		        if($(this).val()=='' || ($(this).val() == null)){
		        	i++;
		        	$(this).attr("style","border-bottom: 2px solid #f00 !important;");
		        }else{			        	
		        	$(this).attr("style","border-bottom: 2px solid #616161 !important");
		        }
		    });
			
			if(i>0){
				alert("Please fill all required fields");
			}
			else{
				new InsertValsEmployementInfo();
				setTimeout(function(){ 
					new OfferSummary();
					// new EmployementInfo();
					 $(".o_next_step").click();
					$(".o_next_step").hide();
				},500);
			}
		}
		if($(this).attr('data_page_id')=='6'){
			var i=0;
		    $(".offer_summary_info .required_cls").each(function(){
		        if($(this).val()=='' || ($(this).val() == null)){
		        	i++;
		        	$(this).attr("style","border-bottom: 2px solid #f00 !important;");
		        }else{			        	
		        	$(this).attr("style","border-bottom: 2px solid #616161 !important");
		        }
		    });
			
			if(i>0){
				alert("Please fill all required fields");
			}
			else{
				new InsertValsOfferSummary();
				setTimeout(function(){ 
					new BackgroundCheck();	
					$(".o_next_step").click();
					$(".o_next_step").hide();
				},500);
			}
		}
		if($(this).attr('data_page_id')=='7'){
			new InsertValsBackgroundVerification();
			setTimeout(function(){
			$(".o_next_step").click();
			$(".o_next_step").hide();
			},1000);
		}
		if($(this).attr('data_page_id')=='8'){
			var i=0;
			 $(".background_info .required_cls").each(function(){
			        if($(this).val()=='' || ($(this).val() == null)){
			        	i++;
			        	$(this).attr("style","border-bottom: 2px solid #f00 !important;");
			        }else{			        	
			        	$(this).attr("style","border-bottom: 2px solid #616161 !important");
			        }
			    });
				
				if(i>0){
					alert("Please fill all required fields");
				}
				else{
					new InsertValsBackgroundCheck();
					setTimeout(function(){ 
						new DocumentCheck();	
						$(".o_next_step").click();
						$(".o_next_step").hide();
					},500);
				}
		}
		if($(this).attr('data_page_id')=='9'){
			new InsertDocumentCheck();
			setTimeout(function(){
			new SummaryBackgroundCheck();
// new HireSummary();
			$(".o_next_step").click();
			$(".o_next_step").hide();
			},1000);
		}
		if($(this).attr('data_page_id')=='10'){
					new InsertRecordSummaryBackgroundCheck();
// new CreateEmployee();
					setTimeout(function(){ 
						new HireSummary();
// new BenefitsEligibility();
						$(".o_next_step").click();
						$(".o_next_step").hide();
					},500);
		}
		if($(this).attr('data_page_id')=='11'){
			new CreateEmployee();
// new WelcomeMail();
			setTimeout(function(){ 
				new BenefitsEligibility();
// new BenefitsEligibility();
				$(".o_next_step").click();
				$(".o_next_step").hide();
			},1000);
		}
		if($(this).attr('data_page_id')=='12'){
			new InsrtValsBenefitsEligibility();
			setTimeout(function(){ 
				new WelcomeMail();
				$(".o_next_step").click();
				$(".o_next_step").hide();
			
			});
		}
		if($(this).attr('data_page_id')=='13'){
			new SendWelcomeMail();
		}
		if($(this).attr('data_page_id')=='14'){
			new onboadinginfo();
			$(".o_next_step").click();
			$(".o_next_step").hide();
// $(".o_next_step").click();
// $(".o_next_step").hide();
		}
		
		if($(this).attr('data_page_id')=='15'){
			new Insertonboadinginfo();
			setTimeout(function(){ 
				new AppraisalInfo();	
				$(".o_next_step").click();
				$(".o_next_step").hide();
			},500);
		}
		
		if($(this).attr('data_page_id')=='16'){
			new InsertValsAppraisalInfo();
			setTimeout(function(){ 
				new EmployeeInfo();	
				$(".o_next_step").click();
				$(".o_next_step").hide();
			},500);
// new CreateContract();
		}
		if($(this).attr('data_page_id')=='17'){
			new Contract();
			$(".o_next_step").click();
			$(".o_next_step").hide();
		}
		if($(this).attr('data_page_id')=='19'){
			new ContractInfo();
			$(".o_next_step").click();
			$(".o_next_step").hide();
		}
		if($(this).attr('data_page_id')=='19'){
			new Complete();
			setTimeout(function(){ 
				$(".o_next_step").click();
				$(".o_next_step").hide();
			},500);
		}
		
		
});
	

		 });	

});