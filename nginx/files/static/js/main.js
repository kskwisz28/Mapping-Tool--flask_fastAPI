// init and globals
//'use strict';

var App = {
    // global app variable
    state: {
        is_country_selected: false,
        is_region_selected: false,
        is_city_selected: false,
        is_concept_selected: false,
        is_location_selected: false,
        is_new_mapping_validated: false,
        lower_concepts: false, 
        higher_concepts: false,
        sort: "pagerank",
        // which are lower in the hierarchy
    },
    inputs: {
        location_id: '',
        country_id: '',
        region_id: '',
        city_id: '',
        concept_id: ''
    },
    templates: {
        concepts_list: '',
        concept_info: '',
        concept_deactivate: '',
        concept_activate: '',
        add_new_mapping: '',
        add_mapping_confirm: '',
        new_mapping_added: '',
        dropdown: '',
        spinner: '',
        confirm_buttons: '',
        close_buttons: ''
        
    },

    
    // call_api: function(url){
        
    //     $.ajax({
    //         'async': true,
    //         'url': url,
    //         'type': 'GET',
    //         'cache': false,
    //         'dataType': 'json',
    //         'success': function(response) {
    //             // console.log('SUCCESS');
    //             if (response.data) {
    //                 return response;
    //             }
    //             else if (response.error){
    //                 console.log('Error getting data from API');
    //                 $("#results-panel").html(response.error);
    //             }
    //         },
    //         'error': function(jq, status, error){
    //             console.log('Error calling API:', status, ' text:', error);
    //         },
    //         'complete': function(jq, status) {
    //             console.log('Api for ', url, ' Result:', status, 'jq:', jq);
    //         }
    //     });
    //}
    
}


function build_results(response, page_id){
    // build search results
    // expecting data to be filled with concepts and locations
    // console.log('Building results...');
    $('#results-panel').html(App.templates.spinner);
    if (response.data.length == 0){
        response.nodata = true;
    }
    response.parse_location = function(){
        return this.locations['l']['location_id'];
    }
    response.parse_concept_name = function(){
        return this.concept.concept_id.replaceAll('_', ' ');
    }
    response.parse_state = function(){
        if (this.concept['banned'] == true){
            return false;
        } else {
            if (this.state){
                return "checked";
            } else {
                return false;
            }
        }
    }

    response.sort_order = function(){
        if (App.state.sort.charAt(0) == '-'){
            return "oi-sort-ascending";
        } else {
            return "oi-sort-descending";
        }
    }
    response.name_sort = function(){
        if (App.state.sort == "name") {
            return "-name";
        }
        else if (App.state.sort == "-name") {
            return "name";
        } 
        return false;
    }
    response.pagerank_sort = function(){
        if (App.state.sort == "pagerank") {
            return "-pagerank";
        }
        else if (App.state.sort == "-pagerank") {
            return "pagerank";
        } 
        return false;
    }
    response.state_sort = function(){
        if (App.state.sort == "state") {
            return "-state";
        }
        else if (App.state.sort == "-state") {
            return "state";
        } 
        return false;
    }

    response.parse_state_deactive = function(){
        if (this.concept['banned'] == true){
            return false;
        } else {
            if (this.state){
                return false;
            } else {
                return true;
            }
        }
    }
    
    response.concept_banned = function(){
        if (this.concept['banned'] == true){
            return true;
        } else {
            return false;
        }
    }
    response.parse_rank = function(){
        if ("pagerank" in this.concept){
            rank = this.concept.pagerank.toFixed(0);
        } else {
            rank = 0;
        }
        return rank;
    }
    response.parse_description = function(){
        if (this.concept.description){
            description = this.concept.description.substr(0, 500);
        } else {
            description = "";
        }
        return description;
    }
    response.count_to = function(){
        return this.skip + this.count - 1;
        // return count_to;
    }
    let rendered = Mustache.render(App.templates.concepts_list, response);
    $('#results-panel').html(rendered);
    // lets add some events
    // change state:
    $('.change-state-btn').click(function(e) {
	e.preventDefault();
	e.stopPropagation();
        let concept_id = $(this).data("concept-id");
        let location_id = $(this).data("location-id");
        
        let concept_state = $(this).data("state");
        change_state_modal(concept_id, location_id, concept_state);
        // show modal window for deactivating/activting concept
    });
    // pagination
    $(".page-link").on("click", function(){
        let page_id = $(this).data('page-id');
        list_concepts(page_id);
    });
    $('.add-mapping').on("click", function(){
        add_new_mapping();
    });

}


function list_concepts(page_id = 1, manual = false, concept_id = false, order=false){
    if (manual == true){ // user click search btn
        App.state.lower_concepts = false;
        App.state.higher_concepts = false;
    }
    if (concept_id) {
        App.state.is_concept_selected = true;
        App.inputs.concept_id = concept_id;
        if (order == 'lower') {
            App.state.lower_concepts = true;
        }
        if (order == 'higher') {
            App.state.higher_concepts = true;
        }
        $('.select-concept').val(concept_id);
        $('#concept-tab').tab('show');
    }
    // get concepts depends on selected location/concept_id/region
    if (App.state.lower_concepts == true) {
        console.log('Lower concepts');
        var url = '/api/get/lower-higher-concepts?concept_id=' +
            App.inputs.concept_id + '&lower=true';
    } else if (App.state.higher_concepts == true){
        console.log('Higher concepts');
        var url = '/api/get/lower-higher-concepts?concept_id=' +
            App.inputs.concept_id + '&lower=false';
    }
    else if (App.state.is_concept_selected == true){
        console.log(App.inputs.concept_id);
        var url = '/api/get/concepts-by-name?concept_id=' +
            App.inputs.concept_id;//
    } else if (App.state.is_city_selected == true){
        var url = '/api/get/concepts-by-city?city_id=' +
            App.inputs.city_id + '&country_id=' +
            App.inputs.country_id +
            '&region_id=' + App.inputs.region_id;
    } else if (App.state.is_region_selected == true) {
        var url = '/api/get/concepts-by-region?region_id=' +
            App.inputs.region_id + '&country_id=' +
            App.inputs.country_id;
    } else if (App.state.is_country_selected == true){
        console.log('Concepts by countries list');
        var url = '/api/get/concepts-by-country?country_id=' +
            App.inputs.country_id;
    } else if (App.state.is_location_selected == true){
        var url = '/api/get/concepts-by-location?location_id=' +
            App.inputs.location_id;
    } else {
        var url = '/api/list/concepts?1=1'; // all concepts
    }
    url = url + "&page_id=" + page_id + "&sort=" + App.state.sort;
    console.log(App.state);
    $('#results-panel').html(App.templates.spinner);

    $.ajax({
        'async': true,
        'url': url,
        'type': 'GET',
        'cache': false,
        'dataType': 'json',
        'success': function(response) {
            // console.log('SUCCESS');
            if (response.data) {
                console.log('Building concepts list');
                build_results(response)
            }
            else if (response.error){
                console.log('Error getting data from API');
                $("#results-panel").html(response.error);
            }
        },
        'error': function(jq, status, error){
            console.log('Error calling API:', status, ' text:', error);
        },
        'complete': function(jq, status) {
            console.log('Api for ', url, ' Result:', status, 'jq:', jq);
        }
        
    });
    
}


function add_new_mapping(){
    $('body').append(App.templates.add_new_mapping);
    $("#add_new_mapping_modal").modal();
    init_forms(); // init dropdown and so on

    if (App.state.is_location_selected) {
        $('.select-location').val(App.inputs.location_id);
    }
    if (App.state.is_country_selected) {
        $('.select-country').val(App.inputs.country_id);
        $(".select-region").prop('disabled', false);
    }
    if (App.state.is_region_selected) {
        $('.select-region').val(App.inputs.region_id);
        $(".select-city").prop('disabled', false);
    }
    if (App.state.is_city_selected) {
        $('.select-city').val(App.inputs.city_id);
    }

    
    add_mapping_win = $('#add_new_mapping_modal');
    add_mapping_win.find(".btn-primary").on("click", function(){
        if (App.state.is_new_mapping_validated){ // saving new mapping
            api_url = '/api/map-new-concept/?concept_id=' +
                $("#concept_id_input_validated").val() +
                '&location_id=' +
                $('#location_id_input_validated').val();

            $.ajax({
                'url': api_url,
                'type': 'PUT',
                'dataType': 'json',
                'success': function(response) {
                    console.log('New mapping:', response);
                    let rendered = Mustache.render(
                    App.templates.new_mapping_added,
                        response
                    );
                    $('#add-mapping-modal-body').html(rendered);
                    $('#add_new_mapping_modal .btn-primary:first').hide();
                    $('#add_new_mapping_modal .btn-secondary:first').html('Close');
                    
                    
                }
            });
            
            return; // FIXME

            
        } 
        // process adding new mapping
        console.log(App.state);
        console.log(App.inputs);
        let is_form_valid = true;
        
        api_url = "/api/check-map-concept/";
        if (App.state.is_location_selected) { //
            api_url += "?location_id=" + App.inputs.location_id;
        } else if (App.state.is_country_selected) {
            api_url += "?country_id=" + App.inputs.country_id;
            if (App.state.is_region_selected) {
                api_url += "&region_id=" + App.inputs.region_id;
                if (App.state.is_city_selected) {
                    api_url += "&city_id=" + App.inputs.city_id;
                }
            }
        } else {
            is_form_valid = false;
            $('#no-location-selected').show();
        }
        if (App.state.is_concept_selected) {
            api_url += "&concept_id=" + App.inputs.concept_id;
        } else {
            is_form_valid = false;
        }
        console.log('Api call', api_url);
        $('#add-mapping-modal-body').html(App.templates.spinner);
        
        $.ajax({
            'url': api_url,
            'type': 'PUT',
            'dataType': 'json',
            'success': function(response) {
                response.concept_id = concept_id;
                let rendered = Mustache.render(
                    App.templates.add_mapping_confirm,
                    response
                );
                $('#add-mapping-modal-body').html(rendered);
                $('#spinner').remove();
                if (response['validated'] == true){
                    App.state.is_new_mapping_validated = true;
                    $('#add_new_mapping_modal .btn-primary:first').html('Confirm');

                    console.log('New mapping is validated');
                } else {
                    App.state.is_new_mapping_validated = false;
                }
            }
        });

    });
}

function expand(element_id, concept_id){
    // expand concept information in table
    // load additional information
    let table_row = document.getElementById(element_id);
    let expanded_row = $(table_row).next('tr');
    $(table_row).find('td:first span').toggleClass('oi-chevron-bottom');
    $(table_row).find('td:first span').toggleClass('oi-chevron-right');
    $(expanded_row).toggle();
    let is_loaded = $(table_row).attr('is_loaded');
    if (!is_loaded == '1') {
        $(expanded_row).append(App.templates.spinner);
        $.ajax({
            'url': '/api/concept-info/?concept_id=' + concept_id,
            'type': 'GET',
            'dataType': 'json',
            'success': function(response) {
                response.concept_id = concept_id;
                let rendered = Mustache.render(
                    App.templates.concept_info,
                    response
                );
                $(expanded_row).find('td:last').append(rendered);
                $(table_row).attr('is_loaded', "1");
                $('#spinner').remove();
            }
        });
    }
}


function change_state_modal(concept_id, location_id, concept_state){
    console.log('>>>LOC;', location_id);
    if (concept_state == "active") {
        template = App.templates.concept_deactivate;
    } else {
        template = App.templates.concept_activate;
    }
    let rendered = Mustache.render(
        template,
        {"concept_id": concept_id,
         "location_id": location_id}
    );
    $('body').append(rendered);
    $("#change_state_modal").modal();
    var modal = $("#change_state_modal");
    modal.find(".btn-primary").on("click", function(){
        // User click Yes, so we need to toggle state of the Concept
        $(this).attr('disabled', true);
        modal.find('.modal-body').html(App.templates.spinner);
        if (concept_state == "active"){
            console.log('Deactivating concept:', concept_id);
            action = "deactivate";
        }
        if (concept_state == "inactive"){
            // console.log('Activating concept:', concept_id);
            action = "activate";
        }
        url = '/api/concept-change-state/?concept_id=' +
            concept_id + '&location_id=' +
            location_id + '&action='+action;
        // console.log('Api call:', url);
        $.ajax({
            'url': url, 
            'type': 'PUT',
            'dataType': 'json',
            'success': function(response) {
                let concept_switch = $("#"+concept_id+"-"+location_id+"-switch");
                if (concept_state == "inactive"){
                    concept_switch.prop("checked", true);
                    concept_switch.data('state', 'active');
                } else {
                    concept_switch.prop("checked", false);
                    concept_switch.data('state', 'inactive');
                }
                modal.modal('hide');
            }
        });

        
    });
}

function select_item(element){
    // dropdowns processing
    let parent = $(element).data('input-source');
    console.log('Parent:', parent);
    $('.' + parent).val($(element).data('name'));
    let name = $(element).data('name');
    $(element).data('encoded-name', encodeURIComponent($(element).data('name')));

    if (parent == 'select-location'){
        clear_all();
        App.inputs.location_id = name;
        $('input.select-location').val(name);
        App.state.is_location_selected = true;
    }
    if (parent == 'select-country'){
        clear_all();
        $('input.select-country').val(name);
        App.state.is_country_selected = true;
        App.inputs.country_id = name;
        $(".select-region").prop('disabled', false);
        $(".select-region").val('');
        App.state.is_region_selected = false;
        App.inputs.region_id = '';
    }
    if (parent == 'select-region'){
        $('input.select-region').val(name);
        App.state.is_region_selected = true;
        App.inputs.region_id = name;
        App.inputs.city_id = '';
        App.state.is_city_selected = false;
        $(".select-city").prop('disabled', false);
        $(".select-city").val('');
    }
    if (parent == 'select-city'){
        $('input.select-city').val(name);
        App.state.is_city_selected = true;
        App.inputs.city_id = name;
        $(".select-city").prop('disabled', false);
    }
    if (parent == 'select-concept'){
        $('input.select-concept').val(name);
        App.state.is_concept_selected = true;
        App.inputs.concept_id = name;
        console.log('Concept select:', App.state);
    }
}


function init_forms(){
    // autocompletes for all inputes
    
    $('.form-control').each(function(i, elem){
        //let data_type = ;
        // go trough inputs
        let data_type = $(elem).data('type');
        if ($(elem).data('toggle') == 'dropdown'){
            // all inputs cleared by DEL key:
            $(elem).on('keydown', function() {
                var key = event.keyCode || event.charCode;
                if( key == 46 ){
                    $(elem).val('');
                    $('.dropdown-menu').removeClass('show');
                    $('.dropdown-menu').html(''); // clear dropdowns
                }
                if (data_type == 'select-city') {
                    App.state.is_city_selected = false;
                    App.inputs.city_id = '';
                }
                if (data_type == 'select-region') {
                    App.state.is_city_selected = false;
                    App.state.is_region_selected = false;
                    App.inputs.city_id = '';
                    App.inputs.region_id = '';
                }
                if (data_type == 'select-city') {
                    App.state.is_city_selected = false;
                }
                
                if( key == 13 ){
                    if (data_type == "location"){
                        App.state.is_location_selected = true;
                        App.inputs.location_id = $('.select-location').val();
                    }
                    list_concepts(1, true);
                }

            });
        }
        
        $(elem).on("input click", function(){
            // const params = new URLSearchParams(App.inputs);
            // console.log(params.toString());
            
            var name = encodeURIComponent($(elem).val() || '');
            console.log('Searching  for name: ', name);
            console.log('SELECTING:', data_type);
            if (data_type == "select-location"){
                // App.state.is_country_selected = false;
                // App.state.is_region_selected = false;
                // App.state.is_city_selected = false;
                // App.state.is_concept_selected = false;
                // App.state.is_location_selected = true;
                // App.state.is_new_mapping_validated = false;
                // App.state.lower_concepts = false;
                // App.state.higher_concepts = false;
                // //sort: "pagerank",
                // App.inputs.country_id = '';
                // App.inputs.region_id = '';
                // App.inputs.city_id = '';
                // App.inputs.concept_id = '';
                
                api_url = '/api/get/locations?skip=0&limit=10&name=';
            }
            if (data_type == "select-country"){
                api_url = '/api/get/countries?skip=0&limit=10&name=';
            }
            if (data_type == "select-region"){
                let country_id = $('input.select-country').val();
                api_url = '/api/get/regions?skip=0&limit=10&country_id='+country_id+'&name=';
            }
            if (data_type == "select-city"){
                let country_id = $('input.select-country').val();
                let region_id = $('input.select-region').val();
                api_url = '/api/get/cities?skip=0&limit=10&country_id=' +
                    country_id + '&region_id=' + region_id + '&name=';
            }
            if (data_type == "select-concept"){
                api_url = '/api/get/concepts?skip=0&limit=10&name='
            }
            console.log(elem);

            
            $.ajax({
                'url': api_url + name,
                'type': 'GET',
                'dataType': 'json',
                'success': function(response) {
                    if (response.data) {
                        response.input_source = data_type; 
                        let rendered = Mustache.render(App.templates.dropdown, response);
                        $('.' + data_type + '-dropdown').html(rendered);
                        $('.' + data_type).on('click', function(){
                            select_item(this);
                        });
                        $('.' + data_type + '-dropdown').dropdown();
                    } else {
                        $('.' + data_type + '-dropdown').html('Nothing found');
                    }
                }
            });
            
        });
    });
}


function load_templates(templates){
    // load templates at initial state
    // so we can render and populate them with
    // corresponding values at runtime
    let v = 1;
     $.get('/templates/concepts-list-table.html?ver='+v, function(data){
         templates.concepts_list = data;
     });
     $.get('/templates/concept-info.html?ver='+v, function(data){
         templates.concept_info = data;
     });
     $.get('/templates/deactivate-concept.html?ver='+v, function(data){
         templates.concept_deactivate = data;
     });
     $.get('/templates/activate-concept.html?ver='+v, function(data){
         templates.concept_activate = data;
     });
     $.get('/templates/add-new-mapping.html?ver='+v, function(data){
         templates.add_new_mapping = data;
     });
     $.get('/templates/spinner.html?ver='+v, function(data){
         templates.spinner = data;
     });
     $.get('/templates/dropdown.html?ver='+v, function(data){
         templates.dropdown = data;
     });
     $.get('/templates/add-mapping-confirm.html?ver='+v, function(data){
         templates.add_mapping_confirm = data;
     });
     $.get('/templates/new-mapping-added.html?ver='+v, function(data){
         templates.new_mapping_added = data;
     });

     $.get('/templates/confirm-buttons.html?ver='+v, function(data){
         templates.confirm_buttons = data;
     });
     $.get('/templates/close-buttons.html?ver='+v, function(data){
         templates.close_buttons = data;
     });
}


// ------------------
// helpers functions:
// ------------------

function clear_city(){
    $('.select-city').val('');
    $(".select-city").prop('disabled', true);
    $('.select-city-dropdown').html('');
    App.state.is_city_selected = false; 
    
}
function clear_regions(){
    clear_city();
    $('.select_region').val('');
    $(".select-region").prop('disabled', true);
    $('.select-region-dropdown').html('');                 
    App.state.is_region_selected = false;
}

function clear_all(){
    // clear all inputs add app state
    $('.dropdown-menu').html('');
    // $(".select-concept").val('');
    $('.select-country').val('');
    $('.select-location').val('');
    $('.select-concept').val('');
    $('.select-region').val('');
    $('.select-country-dropdown').html('');                 
    clear_regions();

    App.state.is_country_selected = false;
    App.state.is_region_selected = false;
    App.state.is_city_selected = false;
    App.state.is_concept_selected = false;
    App.state.is_location_selected = false;
    App.state.is_new_mapping_validated = false;
    App.state.lower_concepts = false;
    App.state.higher_concepts = false;
    App.inputs.country_id = '';
    App.inputs.region_id = '';
    App.inputs.city_id = '';
    App.inputs.concept_id = '';
    App.inputs.location_id = '';
    
    App.state.is_country_selected = false;
    //App.state.is_concept_selected = false;
    App.state.is_location_selected = false;
    
}


function get_query_var(variable) {
    var query = window.location.search.substring(1);
    var vars = query.split('&');
    for (var i = 0; i < vars.length; i++) {
        var pair = vars[i].split('=');
        if (decodeURIComponent(pair[0]) == variable) {
            return decodeURIComponent(pair[1]);
        }
    }
}
function tab(){
    // this function called when user selects tab
    clear_all();
    App.state.is_concept_selected = false;
    App.state.sort = "pagerank";
    App.inputs.concept_id = "";
}

function sort(sort_param, old_sort = false){
    if (old_sort == 'false'){
        old_sort = false;
    }
    if (old_sort){
        App.state.sort = old_sort;
    } else {
        App.state.sort = sort_param;
    }
    console.log('Sort:', App.state.sort);
    list_concepts();
}

// init home page
$(document).ready(function () {

    load_templates(App.templates);
    init_forms();

    if (concept_id = get_query_var('concept_id')) {
        // Show concepts by selected concept
        console.log('concept_id selected');
        App.state.is_concept_selected = true;
        App.inputs.concept_id = concept_id;
        $('#concept-tab').tab('show');
        $('input.select-concept').val(concept_id);
        if (lower_concepts = get_query_var('lower')){
            console.log(App.state.lower_concepts);
            if (lower_concepts == "true"){
                App.state.lower_concepts = true;
                App.state.higher_concepts = false;
            }
        } else if (get_query_var('higher') == "true"){
            App.state.lower_concepts = false;
            App.state.higher_concepts = true;
        }
        list_concepts();
        
    } else {
        //list_concepts(1); // home page with all concepts sorted by rank
    }
});

