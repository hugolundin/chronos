function contains(str, substr) {
  /*
  Return true if str contains substr
  */
  return str.indexOf(substr) > -1
}

function filterTeachersByName(name) {
  /*
  Search for teachers with a specific name and only show relevant results
  */
  var teachers = $('.teacher')
  name = name.toLowerCase()

  teachers.each(function() {
    var firstName = this.children[0].innerText.toLowerCase()
    var lastName = this.children[1].innerText.toLowerCase()

    // Only show relevant teachers in UI
    if (contains(firstName, name) || contains(lastName, name)) {
      $(this).show()
    } else {
      $(this).hide()
    }
  })
}

$(document).ready(function() {
  var search = $('#search')
  search.focus()

  search.on('input', function(e) {
    filterTeachersByName(search.val())
  })

  search.on('keydown', function(e) {
    if (e.keyCode === 13) {
      filterTeachersByName(search.val())
      search.val('')
    }
  })
})
