$(document).ready(function () {
    flight_id = 0;
    hotel_id = 0;
    place_id = 0;

    $("#flight_selected").click(function (event) {
        event.preventDefault();
        flight_id = flight_id + 1;
        flight_id_str = 'flight_' + String(flight_id);

        var newFlightField = '<span id="' + flight_id_str + '">' +
                                '<div class="form-group col-sm-5">' +
                                '    <label for="flight">Flight Number:</label>' +
                                '    <input type="text" class="form-control" id="flight" name="flight" required />' +
                                '</div>' +
                                '<div class="form-group col-sm-5">' +
                                '    <label for="flight_datetime">Flight Date/Time:</label>' +
                                '    <input type="datetime-local" class="form-control" id="flight_datetime" name="flight_datetime" required />' +
                                '</div>' +
                                '<div class="form-group col-sm-1 pull-right">' +
                                '   <label for="single_delete_flight">&nbsp;</label>' +
                                '   <button type="button" class="btn btn-default" id="single_delete_flight" onclick=$(this).closest(' + flight_id_str + ').remove();><span class="glyphicon glyphicon-remove"> </span></button>' +
                                '</div>' +
                              '</span>';
        
        $("#field_table").append(newFlightField);
        console.log("flight...");
        
    });



    $("#hotel_selected").click(function (event) {
        event.preventDefault();
        place_id = place_id + 1;
        place_id_str = 'flight_' + String(place_id);

        var newHotelField = '<span  id="' + place_id_str + '">' +
                        '<div class="form-group col-sm-5">' +
                        '    <label for="hotel">Hotel Info:</label>' +
                        '    <input type="text" class="form-control" id="hotel" name="hotel" required />' +
                        '</div>' +
                        '<div class="form-group col-sm-5">' +
                        '    <label for="hotel_datetime">Hotel Date/Time:</label>' +
                        '    <input type="datetime-local" class="form-control" id="hotel_datetime" name="hotel_datetime" required />' +
                        '</div>' +
                        '<div class="form-group col-sm-1 pull-right">' +
                        '   <label for="single_delete_hotel">&nbsp;</label>' +
                        '   <button type="button" class="btn btn-default" id="single_delete_hotel" name="single_delete_hotel" onclick=$(this).closest(' + place_id_str + ').remove();><span class="glyphicon glyphicon-remove"> </span></button>' +
                        '</div>' +
                        '</span>';

        $("#field_table").append(newHotelField);

        console.log("hotel...")
    });
    $("#place_selected").click(function () {
        event.preventDefault();
        hotel_id = hotel_id + 1;
        hotel_id_str = 'flight_' + String(hotel_id);

        var newPlaceField = '<span  id="' + hotel_id_str + '">' +
                        '<div class="form-group col-sm-5">' +
                        '    <label for="place">Place to Visit:</label>' +
                        '    <input type="text" class="form-control" id="place" name="place" required />' +
                        '</div>' +
                        '<div class="form-group col-sm-5">' +
                        '    <label for="place_datetime">Place Date/Time:</label>' +
                        '    <input type="datetime-local" class="form-control" id="place_datetime" name="place_datetime" required />' +
                        '</div>' +
                        '<div class="form-group col-sm-1 pull-right">' +
                        '   <label for="single_delete_place">&nbsp;</label>' +
                        '   <button type="button" class="btn btn-default" id="single_delete_place" name="single_delete_place" onclick=$(this).closest(' + hotel_id_str + ').remove();><span class="glyphicon glyphicon-remove"> </span></button>' +
                        '</div>' +
                        '</span>'

        $("#field_table").append(newPlaceField);

        $('#single_delete_place').click(function () {
            console.log("clicked remove button")
            $(this).closest('span').remove();
        });

        console.log("place...")
    });
});