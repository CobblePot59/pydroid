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

function rootEmulator(name) {
    $.post('/rootEmulator', { sname: name }, function(data) {
    });
}

// function addCA(name) {
//     $.post('/addCA', { sname: name }, function(data) {
//     });
// }

// function addFrida(name) {
//     $.post('/addFrida', { sname: name }, function(data) {
//     });
// }