/*
 * SPDX-FileCopyrightText: 2022 Magenta ApS
 * SPDX-License-Identifier: MPL-2.0
 */
import { group } from 'k6';
import { client } from '../util.js';

function version() {
  client.get('/version/');
}

function health() {
  client.get('/health/');
}

function org() {
  client.get('/service/o/');
}

export default function apiServiceMetaTests() {
  group('api.service.meta', () => {
    version();
    org();
  });
  group('api.service.meta.health', () => {
    health();
  });
}
