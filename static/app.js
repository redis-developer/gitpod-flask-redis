window.onload = function () {
  const resetBtn = document.getElementById('resetBtn');
  const checkBloom = document.getElementById('checkbloom');
  const checkSet = document.getElementById('checkset');
  const addBloom = document.getElementById('addbloom');
  const addSet = document.getElementById('addset');
  const addthing = document.getElementById('addthing');
  const checkthing = document.getElementById('checkthing');
  const pop = document.getElementById('populate');

  const updateData = async function (relativePath) {
    const response = await fetch(relativePath);
    const responseJSON = await response.json();
    const checkElem = document.getElementById('checkValue');
    const timeElem = document.getElementById('timeValue');
    checkElem.innerText = responseJSON.check;
    timeElem.innerText = responseJSON.time;
  }

  pop.onclick = async function () {
    await updateData('/pop')
  }

  addBloom.onclick = async function () {
    addThing = addthing.value
    await updateData(`/addbloom/${addThing}`)
  }

  addSet.onclick = async function () {
    addThing = addthing.value
    await updateData(`/addset/${addThing}`)
  }

  checkBloom.onclick = async function () {
    checkThing = checkthing.value
    await updateData(`/checkbloom/${checkThing}`)
  }

  checkSet.onclick = async function () {
    checkThing = checkthing.value
    await updateData(`/checkset/${checkThing}`)
  }

  resetBtn.onclick = async function () {
    await updateData('/reset');
  }
}