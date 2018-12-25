# -*- coding: utf-8 -*-
from ..logger import logger
from ..models import BankBranch


def branch_data():
    """返回银行对应数据
    """
    branches = BankBranch.objects.filter(is_use=True, is_map=True)
    ret_branches = []
    ret_counties = set()
    for branch in branches:
        ret_branches.append({
            'id': branch.id,
            'name': branch.name,
            'longitude': str(branch.longitude),
            'latitude': str(branch.latitude),
            'address': branch.address,
            'county': branch.country,
            'waitman': branch.waitman,
            'telno': branch.telno,
            'officehours': branch.officehours,
        })
        ret_counties.add(branch.country)
    return {'success': True, 'branches': ret_branches, 'counties': list(ret_counties)}
