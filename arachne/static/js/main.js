window.onload = function() {
    // Only set prevWindow if currWindow exists
    const currUrl = window.location.href;
    const prevUrl = sessionStorage.getItem('currWindow');

    if (prevUrl && prevUrl !== currUrl) {
        sessionStorage.setItem('prevWindow', prevUrl);
    }

    // Always update currWindow
    sessionStorage.setItem('currWindow', currUrl);
}

function goBack() {
    const prevUrl = sessionStorage.getItem('prevWindow');
    if (prevUrl != window.location.href) {
        window.location.assign(prevUrl);
    } else {
        window.location.assign('/');
    }
}

//Modal for deletion of object
function deleteConfirm(id, type){
    modalText = "This action is irreversible, are you sure you want to delete this link?"
    const modal = document.getElementById('modal_background')
    const modal_text = document.getElementById('modal_content')
    const modal_del = document.getElementById('modal_delete')

    modal.style.display = "block"
    modal_text.innerHTML = modalText
    document.getElementById('modal_delete').addEventListener("click", () => finalConfirm(id, type))

}

//Modal for clearing of Link
function clearConfirm(){
    const modalText = "This action is irreversible, are you sure you want to delete all current links?"
    const modal = document.getElementById('modal_background')
    const modal_text = document.getElementById('modal_content')
    const modal_del = document.getElementById('modal_delete')

    modal.style.display = "block"
    modal_text.innerHTML = modalText
    document.getElementById('modal_delete').addEventListener("click", () => finalConfirm(0))
}

//User Confirmed the deletion
function finalConfirm(id, type=null){
    if(id == 0){
        window.location.assign(`/clear/`)
    }
    else{
        window.location.assign(`/delete/${id}/${type}`)
    }
}

//Close Modal
function cancelModal(){
    const modal = document.getElementById('modal_background')
    modal.style.display = "none"
}
