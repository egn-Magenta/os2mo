import {HTTP, Service} from './HttpCommon'

export default {

  /**
   * Get a list of all employees
   * @returns {Array} List of all employees
   */
  getAll (orgUuid) {
    return Service.get(`/o/${orgUuid}/e/`)
      .then(response => {
        return response.data
      })
      .catch(error => {
        console.log(error.response)
      })
  },

  /**
   * Get an employee
   * @param {String} uuid - uuid for employee
   * @returns {Object} employee object
   */
  getEmployee (uuid) {
    return Service.get(`/e/${uuid}/`)
    .then(response => {
      return response.data
    })
    .catch(error => {
      console.log(error.response)
    })
  },

  /**
   * Get engagement details for employee
   * @param {String} uuid - employee uuid
   * @see getDetail
   */
  getEngagementDetails (uuid) {
    return this.getDetail(uuid, 'engagement')
  },

  /**
   * Get contacts details for employee
   * @param {String} uuid - Employee uuid
   * @see getDetails
   */
  getContactDetails (uuid) {
    return this.getDetails(uuid, 'contact')
  },

  /**
   * Get IT details for employee
   * @param {String} uuid - Employee uuid
   * @see getDetail
   */
  getItDetails (uuid) {
    return this.getDetail(uuid, 'it')
  },

  /**
   * Get association details for employee
   * @param {String} uuid - Employee uuid
   * @see getDetail
   */
  getAssociationDetails (uuid) {
    return this.getDetail(uuid, 'association')
  },

  /**
   * Get leave details for employee
   * @param {String} uuid - Employee uuid
   * @see getDetail
   */
  getLeaveDetails (uuid) {
    return this.getDetail(uuid, 'leave')
  },

  /**
   * Base call for getting details.
   * @param {String} uuid - employee uuid
   * @param {String} detail - Name of the detail
   * @returns {Array} A list of options for the detail
   */
  getDetail (uuid, detail) {
    return Service.get(`/e/${uuid}/details/${detail}`)
    .then(response => {
      return response.data
    })
    .catch(error => {
      console.log(error.response)
    })
  },

  /**
   * Get a list of available details
   * @param {String} uuid - employee uuid
   * @returns {Object} A list of available tabs
   */
  getDetailList (uuid) {
    return Service.get(`e/${uuid}/details/`)
    .then(response => {
      return response.data
    })
    .catch(error => {
      console.log(error.response)
    })
  },

  /**
   * Base call for getting details about an employee.
   * @param {String} uuid - Employee uuid
   * @param {String} detail - Name of the detail to get
   * @param {String} validity - Can be 'past', 'present' or 'future'
   * @returns {Object} Detail data
   * @deprecated
   */
  getDetails (uuid, detail, validity) {
    validity = validity || 'present'
    return HTTP.get(`/e/${uuid}/role-types/${detail}/?validity=${validity}`)
    .then(response => {
      return response.data
    })
    .catch(error => {
      console.log(error.response)
    })
  },

  /**
   * Create a new employee
   * @param {Object} engagement - new Employee uuid
   * @returns {Object} employee uuid
   */
  createEmployee (uuid, engagement, association) {
    return Service.post(`/e/${uuid}/create`, engagement, association)
    .then(response => {
      return response.data
    })
    .catch(error => {
      console.log(error.response)
    })
  },

  /**
   * Move an employee
   * @param {Object} uuid - employee to move
   * @param {String} engagement - uuid for the new employee
   * @returns {Object} employeee uuid
   */
  editEmployee (uuid, engagement) {
    return Service.post(`/e/${uuid}/edit`, engagement)
    .then(response => {
      return response.data
    })
    .catch(error => {
      console.log(error.response)
    })
  },

   /**
   * End an employee
   * @param {Object} engagement - the employee to end
   * @param {String} endDate - the date on which the employee shall end
   * @returns {Object} employee uuid
   */
  endEmployee (uuid, engagement) {
    return Service.post(`/e/${uuid}/terminate`, engagement)
    .then(response => {
      return response.data
    })
    .catch(error => {
      console.log(error.response)
    })
  },

  /**
   * Create a new engagement for an employee
   * @param {String} uuid - Employee uuid
   * @param {Object} engagement - New engagement
   * @deprecated
   */
  createEngagement (uuid, engagement) {
    return HTTP.post(`/e/${uuid}/roles/engagement`, engagement)
    .then(response => {
      console.log(response)
      return response
    })
    .catch(error => {
      console.log(error.response)
    })
  }
}
