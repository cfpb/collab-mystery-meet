function video_style() {
    var value = $('input:radio[name="meet_choice"]:checked').val()
    if ( value === 'video' ) {
        $('.location-list input').attr('disabled', 'true');
        $('.location-list input').removeAttr('checked');
        $('.location-list').css('color', '#CCC');
    }
    else {
        $('.location-list input').removeAttr('disabled');
        $('.location-list').css('color', 'inherit');
    }
}

$(document).ready( function() {
    video_style();
    $('.mystery-form').on('click', 'input:radio[name="meet_choice"]', video_style);
});
