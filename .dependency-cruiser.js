module.exports = {
  forbidden: [
    {
      name: 'no-layer-violations',
      severity: 'error',
      from: { path: '^packages/(contracts-common|contracts-core|contracts-diagnostics|contracts-execution|contracts-events|contracts-provider)' },
      to: { path: '^packages/(spi-provider|kernel-core)' }
    }
  ],
  options: {
    doNotFollow: {
      path: 'node_modules'
    },
    includeOnly: '^packages/'
  }
};