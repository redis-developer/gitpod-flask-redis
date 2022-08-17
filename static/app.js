window.onload = function () {
  const checkFBtn = document.getElementById('checkFilter');
  const addFBtn = document.getElementById('addFilter');
  const checkSBtn = document.getElementById('checkSketch');
  const addSBtn = document.getElementById('addSketch');
  const resetBtn = document.getElementById('resetBtn');
  const popthou = document.getElementById('populate1000');
  const poptenthou = document.getElementById('populate10000');
  const popalot = document.getElementById('populatelots');
  const popusers = document.getElementById('populateusers');

  const updateData = async function (relativePath) {
    const response = await fetch(relativePath);
    const responseJSON = await response.json();
    const checkElem = document.getElementById('checkValue');
    checkElem.innerText = responseJSON.check;
  }

  popthou.onclick = async function () {
    await updateData('/pop/words_1000')
  }

  poptenthou.onclick = async function () {
    await updateData('/pop/words_10000')
  }

  popalot.onclick = async function () {
    await updateData('/pop/words_alpha')
  }

  popusers.onclick = async function () {
    await updateData('/pop/users')
  }

  addSBtn.onclick = async function () {
    var select_sketch = document.getElementById('sketch_type');
    var sketch = select_sketch.value
    var item_to_sketch = document.getElementById('itemS');
    item_to_sketch = item_to_sketch.value
    console.log(sketch)
    switch (sketch) {
      case "TopK":
        await updateData(`/addtopk/${item_to_sketch}`)
        break
      case "CMS":
        await updateData(`/addcms/${item_to_sketch}`)
        break
      case "SortedSet":
        await updateData(`/addsorted/${item_to_sketch}`)
        break
    }
  }

  checkSBtn.onclick = async function () {
    var select_sketch = document.getElementById('sketch_type');
    var sketch = select_sketch.value
    var item_to_sketch = document.getElementById('itemS');
    item_to_sketch = item_to_sketch.value
    switch (sketch) {
      case "TopK":
        await updateData(`/querytopk/${item_to_sketch}`)
        break
      case "CMS":
        await updateData(`/cmsquery/cms/${item_to_sketch}`)
        break
      case "SortedSet":
        await updateData(`/addsorted/${item_to_sketch}`)
        break
    }
  }

  addFBtn.onclick = async function () {
    var select_filter = document.getElementById('filter_type');
    var filter = select_filter.value;
    var item_to_filter = document.getElementById('itemF');
    console.log(item_to_filter.value, filter)
    item_to_filter = item_to_filter.value
    switch (filter) {
      case "Bloom":
        await updateData(`/addbloom/${item_to_filter}`)
        break
      case "Set":
        await updateData(`/addset/${item_to_filter}`)
        break
      case "Cuckoo":
        await updateData(`/addcuckoo/${item_to_filter}`)
        break
    }
  }

  checkFBtn.onclick = async function () {
    var select_filter = document.getElementById('filter_type');
    var filter = select_filter.value;
    var item_to_filter = document.getElementById('itemF');
    item_to_filter = item_to_filter.value
    switch (filter) {
      case "Bloom":
        await updateData(`/checkbloom/${item_to_filter}`)
        break
      case "Set":
        await updateData(`/checkset/${item_to_filter}`)
        break
      case "Cuckoo":
        await updateData(`/checkcuckoo/${item_to_filter}`)
        break
    }
  }

  resetBtn.onclick = async function () {
    await updateData('/reset');
  }
}