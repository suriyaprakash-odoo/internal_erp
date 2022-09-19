odoo.define('ppts_experience', function (require) {
	$(document).ready(function(){

		// $('body').on('focus',".datepicker_custom", function(){
		// 	$(this).datepicker({
		// 		changeMonth: true,
		// 		changeYear: true,
		// 		yearRange: "1940:2100",
		// 		dateFormat: "yy-mm-dd"
		// 	});
		// });

		setTimeout(function(){
			$('.datepicker_custom').datepicker({
				changeMonth: true,
				changeYear: true,
				yearRange: "1940:2100",
				dateFormat: "dd-mm-yy"
			});
		});

			// $('.o_website_form_send').hide();

			$('body').delegate('.js_submit','click',function() {
				var j=0;
				// if (document.getElementById("inputFileToLoad").files.length > 0){
				// 	var filesSelected = document.getElementById("inputFileToLoad").files;
				// 	console.log(filesSelected[0].type);
				// 	if ((filesSelected[0].type != 'application/vnd.openxmlformats-officedocument.wordprocessingml.document') && (filesSelected[0].type != 'application/msword') && (filesSelected[0].type != 'application/pdf') && (filesSelected[0].type != 'application/rtf')){
				// 		j = 1;
				// 		alert('Please select an PDF/Docx/Doc files');
				// 	}
				// 	if ((filesSelected[0].size > '5000000')){
				// 		j = 1;
				// 		 alert('Please select a below 5MB files');
				// 		}
				// }
				var m=1;
				var n=1;
				var req_academic=0;
				var academic_info = []
				$('.academic_exp tr').each(function(){
				var degree = $(this).find(".form_academic_degree").val()
				var study = $(this).find(".form_academic_field_of_study").val()
				var institution = $(this).find(".form_academic_institution").val()
				var percentage = $(this).find(".form_academic_percentage").val()
				var passing = $(this).find(".form_academic_year_of_passing").val()
				
//				if (degree == '' || study == '' || institution =='' || percentage == '' || passing == '' ) {
//					m++;
////					alert('Please Complete the details');
//				}
				if (degree && study && institution &&  percentage && passing) {
					req_academic=0;
				}
				else if (degree || study || institution ||  percentage || passing) {
					req_academic=1;
//					alert('Please Complete the details');
				}
				if(req_academic==1) {
					if (degree == '') {
						$(this).find(".form_academic_degree").attr("style","border-bottom: 2px solid #f00 !important;");
					}	
					else {
						
						$(this).find(".form_academic_degree").attr("style","border-bottom: 2px solid #cfcfcf !important");
					}
					if (study == '') {
						$(this).find(".form_academic_field_of_study").attr("style","border-bottom: 2px solid #f00 !important;");
					}
					else {
						
						$(this).find(".form_academic_field_of_study").attr("style","border-bottom: 2px solid #cfcfcf !important");
					}
					if (institution == '') {
						$(this).find(".form_academic_institution").attr("style","border-bottom: 2px solid #f00 !important;");
					}
					else {
						
						$(this).find(".form_academic_institution").attr("style","border-bottom: 2px solid #cfcfcf !important");
					}
					if (percentage == '') {
						$(this).find(".form_academic_percentage").attr("style","border-bottom: 2px solid #f00 !important;");
					}
					else {
						
						$(this).find(".form_academic_percentage").attr("style","border-bottom: 2px solid #cfcfcf !important");
					}
					if (passing == '') {
						$(this).find(".form_academic_year_of_passing").attr("style","border-bottom: 2px solid #f00 !important;");
					}
					else {
						
						$(this).find(".form_academic_year_of_passing").attr("style","border-bottom: 2px solid #cfcfcf !important");
					}
//					alert('Please Complete the details');
				}
				if(n>=2) {
					academic_info.push([
						$(this).find(".form_academic_exp_tree_id").val(),
						$(this).find(".form_academic_degree").val(),
						$(this).find(".form_academic_field_of_study").val(),
						$(this).find(".form_academic_institution").val(),
						$(this).find(".form_academic_percentage").val(),
						$(this).find(".form_academic_year_of_passing").val()]);
					}
					n++;
					});
				$(".academic_info_arr").val(JSON.stringify(academic_info));
	
			var n=1;
			req_po=0;
			var professional_info = []
			$('.professional_exp tr').each(function(){
				var position = $(this).find(".form_professional_exp_position").val()
				var organ = $(this).find(".form_professional_exp_organization").val()
				var start_date = $(this).find(".form_professional_exp_start_date").val()
				var end_date = $(this).find(".form_professional_exp_end_date").val()
//				if (position == '' || organ == '' || start_date =='' || end_date == '') {
//					m++;
////							alert('Please Complete the details');
//				}
				if (position && organ && start_date && end_date) {
					req_po=0;
//									alert('Please Complete the details');
				}
				else if (position || organ || start_date || end_date) {
					req_po=1;
//							alert('Please Complete the details');
				}
				if(req_po==1) {
					if (position == '') {
						$(this).find(".form_professional_exp_position").attr("style","border-bottom: 2px solid #f00 !important;");
					}
					else {
						
						$(this).find(".form_professional_exp_position").attr("style","border-bottom: 2px solid #cfcfcf !important");
					}
					if (organ == '') {
						$(this).find(".form_professional_exp_organization").attr("style","border-bottom: 2px solid #f00 !important;");
					}
					else {
						
						$(this).find(".form_professional_exp_organization").attr("style","border-bottom: 2px solid #cfcfcf !important");
					}
					if (start_date == '') {
						$(this).find(".form_professional_exp_start_date").attr("style","border-bottom: 2px solid #f00 !important;");
					}
					else {
						
						$(this).find(".form_professional_exp_start_date").attr("style","border-bottom: 2px solid #cfcfcf !important");
					}
					if (end_date == '') {
						$(this).find(".form_professional_exp_end_date").attr("style","border-bottom: 2px solid #f00 !important;");
					}
					else {
						
						$(this).find(".form_professional_exp_end_date").attr("style","border-bottom: 2px solid #cfcfcf !important");
					}
//					alert('Please Complete the details');
				}
				if(n>=2) {
				professional_info.push([$(this).find(".form_professional_exp_tree_id").val(),
					$(this).find(".form_professional_exp_position").val(),
					$(this).find(".form_professional_exp_organization").val(),
					$(this).find(".form_professional_exp_start_date").val(),
					$(this).find(".form_professional_exp_end_date").val()]);
				}
				n++;
				});
			$(".professional_info_arr").val(JSON.stringify(professional_info));
			var n=1;
			var req=0;
			var certification_info = []
			$('.certification_exp tr').each(function(){
				var certificate = $(this).find(".form_certification_exp_certificate").val()
				var issue_by = $(this).find(".form_certification_exp_issued_by").val()
				var start_issued = $(this).find(".form_certification_exp_state_issued").val()
				var start_date = $(this).find(".form_certification_exp_start_date").val()
				var end_date = $(this).find(".form_certification_exp_end_date").val()
//				if (certificate == '' || issue_by == '' || start_issued =='' || start_date == '' || end_date == '') {
//					m++;
////					alert('Please Complete the details');
//				}
				if (certificate && issue_by && start_issued && start_date && end_date) {
					req=0;
//							alert('Please Complete the details');
				}
				else if (certificate || issue_by || start_issued || start_date || end_date) {
					req=1;
//					alert('Please Complete the details');
				}
				if(req==1) {
					if (certificate == '') {
						$(this).find(".form_certification_exp_certificate").attr("style","border-bottom: 2px solid #f00 !important;");
						
					}
					else {
						
						$(this).find(".form_certification_exp_certificate").attr("style","border-bottom: 2px solid #cfcfcf !important");
					}
					if (issue_by == '') {
						$(this).find(".form_certification_exp_issued_by").attr("style","border-bottom: 2px solid #f00 !important;");
						
					}
					else {
						
						$(this).find(".form_certification_exp_issued_by").attr("style","border-bottom: 2px solid #cfcfcf !important");
					}
					if (start_issued == '') {
						$(this).find(".form_certification_exp_state_issued").attr("style","border-bottom: 2px solid #f00 !important;");
						
					}
					else {
						
						$(this).find(".form_certification_exp_state_issued").attr("style","border-bottom: 2px solid #cfcfcf !important");
					}
					if (start_date == '') {
						$(this).find(".form_certification_exp_start_date").attr("style","border-bottom: 2px solid #f00 !important;");
						
					}
					else {
						
						$(this).find(".form_certification_exp_start_date").attr("style","border-bottom: 2px solid #cfcfcf !important");
					}
					if (end_date == '') {
						$(this).find(".form_certification_exp_end_date").attr("style","border-bottom: 2px solid #f00 !important;");
						
					}
					else {
						
						$(this).find(".form_certification_exp_end_date").attr("style","border-bottom: 2px solid #cfcfcf !important");
					}
//					alert('Please Complete the details');
				}
				if(n>=2) {
				certification_info.push([$(this).find(".form_certification_exp_tree_id").val(),
					$(this).find(".form_certification_exp_certificate").val(),
					$(this).find(".form_certification_exp_issued_by").val(),
					$(this).find(".form_certification_exp_state_issued").val(),
					$(this).find(".form_certification_exp_start_date").val(),
					$(this).find(".form_certification_exp_end_date").val()]);
				}
				n++;
				});
			if(req==1 || req_po==1 || req_academic==1) {
				
				alert('Please Complete the details');
			}
			
			$(".certification_info_arr").val(JSON.stringify(certification_info));
			
			var n=1;
			var references_info = []
			$('.referance tr').each(function(){
			if(n>=2) {
				references_info.push([$(this).find(".form_references_tree_id").val(),
				$(this).find(".form_references_name").val(),
				$(this).find(".form_references_relationship").val(),
				$(this).find(".form_references_no_years").val(),
				$(this).find(".form_references_occupation").val(),
				$(this).find(".form_references_annual_income").val(),
				$(this).find(".form_references_phone_number").val()]);
			}
			n++;
			});
			$(".references_info_arr").val(JSON.stringify(references_info));
			// if (req==0 && req_po==0 && req_academic==0) {
			// 	setTimeout(function(){ 		
			// 		alert('------------------------------');
			// 		$('.o_website_form_send').click();
			// 	});
			// }
				});
			$('body').delegate('.add_more_academic','click',function() {
				$(".academic_exp tbody").append('<tr>\
					<td style= "display:none">\
						<input class="input_box form_academic_exp_tree_id"  value="0"  type="text"/>\
					</td>\
					<td>\
						<input class="input_box form_academic_degree"  value=""  type="text" placeholder="Degree" style="border:none" />\
					</td>\
					<td>\
						<input class="input_box form_academic_field_of_study"  value=""  type="text" placeholder="Field of study" style="border:none" />\
					</td>\
					<td>\
						<input class="input_box form_academic_institution"  value=""  type="text" placeholder="Institution" style="border:none" />\
					</td>\
					<td>\
						<input class="input_box form_academic_percentage"  value=""  type="text" placeholder="Percentage" style="border:none" />\
					</td>\
					<td>\
						<input class="input_box form_academic_year_of_passing"  value=""  type="text" placeholder="Year of Passing" style="border:none" />\
					</td>\
					<td class="website_trash"><i class="fa fa-trash"></i></td>\
				</tr>');
				$(".academic_exp tbody").find("tr:last").find(".form_academic_exp_tree_id").val(0);
			});
			
				
			$('body').delegate('.add_more_professional','click',function() {
				$(".professional_exp tbody").append('<tr>\
					<td style="display:none">\
						<input class="input_box form_professional_exp_tree_id"  value="0"  type="text"/>\
					</td>\
					<td>\
						<input class="input_box form_professional_exp_position"  value=""  type="text" placeholder="Position" style="border:none" />\
					</td>\
					<td>\
						<input class="input_box form_professional_exp_organization"  value=""  type="text" placeholder="Organization" style="border:none" />\
					</td>\
					<td>\
						<input class="input_box form_professional_exp_start_date"  value=""  type="date" style="border:none" />\
					</td>\
					<td>\
						<input class="input_box form_professional_exp_end_date"  value=""  type="date" style="border:none" />\
					</td>\
					<td class="website_trash"><i class="fa fa-trash"></i></td>\
				</tr>');
				$(".professional_exp tbody").find("tr:last").find(".professional_exp_offer_accepted").val(0);
			});
			
			$('body').delegate('.add_more_referances','click',function() {
				$(".referance tbody").append('<tr>\
					<td style="display:none">\
						<input class="input_box form_references_tree_id"  value="0"  type="text"/>\
					</td>\
					<td>\
						<input class="input_box form_references_name"  value=""  type="text" placeholder="Name" style="border:none" />\
					</td>\
					<td>\
						<input class="input_box form_references_relationship"  value=""  type="text" placeholder="Relationship" style="border:none" />\
					</td>\
					<td>\
						<input class="input_box form_references_no_years"  value=""  type="text" placeholder="No of Years" style="border:none" />\
					</td>\
					<td>\
						<input class="input_box form_references_occupation"  value=""  type="text" placeholder="Occupation" style="border:none" />\
					</td>\
					<td>\
					<input class="input_box form_references_annual_income"  value=""  type="text" placeholder="Email-ID" style="border:none" />\
					</td>\
					<td>\
					<input class="input_box form_references_phone_number"  value=""  type="text" placeholder="Phone Number" style="border:none" />\
					</td>\
					<td class="website_trash"><i class="fa fa-trash"></i></td>\
				</tr>');
				$(".referance tbody").find("tr:last").find(".form_references_tree_id").val(0);
					});
			$('body').delegate('.add_more_certification','click',function() {
					$(".certification_exp tbody").append('<tr>\
								<td style="display:none">\
									<input class="input_box form_certification_exp_tree_id"\
										value="0" type="text" />\
								</td>\
								<td>\
									<input class="input_box form_certification_exp_certificate"\
										value="" type="text" placeholder="Certifications" style="border:none" />\
								</td>\
								<td>\
									<input class="input_box form_certification_exp_issued_by"\
										value="" type="text" placeholder="Issued By" style="border:none" />\
								</td>\
								<td>\
									<select class="input_box form_certification_exp_state_issued"\
										style="border:none;height: 23px;">\
										<option value="">State Issued</option>\
										<t t-foreach="states" t-as="state">\
											<option t-attf-value="#{ state.id }" t-field="state.name"></option>\
										</t>\
									</select>\
								</td>\
								<td>\
									<input\
										class="input_box form_certification_exp_start_date"\
										value="" type="date" style="border:none" />\
								</td>\
								<td>\
									<input\
										class="input_box form_certification_exp_end_date"\
										value="" type="date" style="border:none" />\
								</td>\
								<td class="website_trash">\
									<i class="fa fa-trash"></i>\
								</td>\
							</tr>');
					$(".certification_exp tbody").find("tr:last").find(".form_certification_exp_tree_id").val(0);
				});
			$('body').delegate('.website_trash','click',function() {
				if($(this).parent().parent().find('tr').length>2){
					$(this).parent().remove();
				}
			});
		         
		      
		});
});