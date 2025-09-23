/**
 * Process data in table form
 * The elements for data scraping, table is a single element, and similar elements are multiple elements
 * For a single element, only one call is needed to obtain the element and data. For multiple elements, a loop call is required to obtain the element and data
 */

import type { SimilarDataType, TableDataType } from '../types/data_batch'

class DataTable {
  public data: TableDataType | SimilarDataType
  private produceType: 'table' | 'similar'
  constructor(params, values, produceType: 'table' | 'similar') {
    this.produceType = produceType
    if (produceType === 'table') {
      this.data = {
        ...params,
        produceType,
        values,
      }
    }
    if (produceType === 'similar') {
      const vals = {
        ...params,
        value: values,
      }
      this.data = {
        produceType,
        values: [vals],
      }
    }
  }

  public getTable() {
    return this.data
  }

  public isSimilarDataType() {
    return this.produceType === 'similar'
  }
}

export default DataTable
