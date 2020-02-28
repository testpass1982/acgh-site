$(document).ready(()=>{
    const rgb2hex = (rgb) => {
        if (rgb.search("rgb") === -1) return rgb;
        rgb = rgb.match(/^rgba?\((\d+),\s*(\d+),\s*(\d+)(?:,\s*(\d+))?\)$/);
        const hex = (x) => ("0" + parseInt(x).toString(16)).slice(-2);
        return "#" + hex(rgb[1]) + hex(rgb[2]) + hex(rgb[3]);
      };

    // console.log('HI ADMIN');
    // $('.rect').click(function(event) {
    //     target = $(event.target);
    //     element = target.closest('.rect')[0];
    //     var color = rgb2hex($(element).css('backgroundColor')).toUpperCase();
    //     var input_colors = $('#id_colors').val();
    // });
    $(document).click(function(event) {
            var target = $(event.target);
            // elements = target.parentsUntil("div").css({'z-index': '1000'});
            // console.log(elements);
            var square = $('div').filter(function(){
                return $(this).css('z-index') == '1000';
             });
            if ($(square[0]).children()[0]) {
                var colors_array = [];
                $('input.rect').each(function(){
                    var color = rgb2hex($(this).css('backgroundColor')).toUpperCase();
                    colors_array.push(color);
                });
                // console.log(colors_array);
                var input_colors = $('input#id_colors').val();
                // console.log(colors_array.join(', '))
                // console.log(input_colors);
                if (input_colors != colors_array.join(', ')) {
                    $('input#id_colors').val(colors_array.join(', '));
                };
            };
            
    });
})
