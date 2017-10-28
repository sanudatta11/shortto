/**
 * Created by sanu on 28/10/17.
 */
var global_gradient = null;
var arr = ['red', 'meridian', 'sunset', 'timbr', 'pre-dawn', 'man-of-steel', 'instagram', 'sage', 'forest', 'deep-space', 'red-ocean', 'disco'];
changeColor('random');

function changeColor(color) {

    switch (color) {
        case 'red':
            if (global_gradient != null) {
                document.body.classList.remove(global_gradient);
            }
            document.body.classList.add('red');
            global_gradient = 'red';
            break;
        case 'meridian':
            if (global_gradient != null) {
                document.body.classList.remove(global_gradient);
            }
            document.body.classList.add('meridian');
            global_gradient = 'meridian';
            break;
        case 'sunset':
            if (global_gradient != null) {
                document.body.classList.remove(global_gradient);
            }
            document.body.classList.add('sunset');
            global_gradient = 'sunset';
            break;

        case 'timbr':
            if (global_gradient != null) {
                document.body.classList.remove(global_gradient);
            }
            document.body.classList.add('timbr');
            global_gradient = 'timbr';
            break;

        case 'random':
            var idx = Math.floor(Math.random() * arr.length);

            if (global_gradient == arr[idx]) {
                idx = (idx + 1) % 11;
            }


            if (global_gradient != null) {
                document.body.classList.remove(global_gradient);
            }


            console.log(idx);
            document.body.classList.add(arr[idx]);
            global_gradient = arr[idx];
            break;
        default:
            break;
    }
}

function copy() {
    var txt = document.getElementById('short_url');
    txt.select();
    document.execCommand("Copy");
    document.getElementById('label_done').innerHTML = 'Your Short URL is made.(Copied)';
    setTimeout(function () {
        document.getElementById('label_done').innerHTML = 'Your Short URL is made.';
    }, 2000)
}
