function removeEmulator(name) {
    $.post('/removeEmulator', { sname: name }, function(data) {
        window.location.reload();
    });
}

function startEmulator(name) {
    $.post('/startEmulator', { sname: name }, function(data) {
    });
}

$('#createEmulatorForm').submit(function(event) {
    $.post('/createEmulator', function(data) {
    });
});