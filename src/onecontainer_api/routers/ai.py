# SPDX-License-Identifier: BSD-3-Clause
#  Copyright (c) 2020 Intel Corporation
"""AI vertical entrypoint."""
import databases
from aiocache import cached
from aiocache import Cache
from fastapi import APIRouter, Depends, File, UploadFile

from onecontainer_api import errors, models, schemas
from onecontainer_api.config import cache_tte
from onecontainer_api.routers import drivers, services

router = APIRouter()


@router.get(
    "/ai/{service_id}/usage", description="Get functions available for this service"
)
async def usage(
    service_id: str,
    sync: bool = False,
    ttl: int = 3600,
    db: databases.Database = Depends(models.get_db),
):
    service = await services.get_service(service_id, db)
    if service.driver:
        driver = await drivers.get_driver(service.driver)
        return drivers.service_stack(
            driver, service, "get", "/usage", sync=sync, ttl=ttl
        )
    raise errors.ServiceException(
        service.id, errors.NO_DRV_ERROR, "Service has no driver assigned"
    )


@router.post("/ai/{service_id}/serve", description="Load a model")
@cached(ttl=cache_tte, cache=Cache.MEMORY)
async def serve(
    service_id: str,
    model_meta: schemas.AIModelMeta,
    sync: bool = False,
    ttl: int = 3600,
    db: databases.Database = Depends(models.get_db),
):
    service = await services.get_service(service_id, db)
    if service.driver:
        driver = await drivers.get_driver(service.driver)
        return drivers.service_stack(
            driver,
            service,
            "post",
            "/serve",
            data=model_meta.dict(),
            sync=sync,
            ttl=ttl,
        )
    raise errors.ServiceException(
        service.id, errors.NO_DRV_ERROR, "Service has no driver assigned"
    )


@router.post(
    "/ai/{service_id}/predict", description="Execute an inference over an image"
)
@cached(ttl=cache_tte, cache=Cache.MEMORY)
async def predict(
    service_id: str,
    image_file: UploadFile = File(...),
    sync: bool = False,
    ttl: int = 3600,
    db: databases.Database = Depends(models.get_db),
):
    service = await services.get_service(service_id, db)
    if service.driver:
        driver = await drivers.get_driver(service.driver)
        return drivers.service_stack(
            driver, service, "post", "/predict", data=image_file, sync=sync, ttl=ttl
        )
    raise errors.ServiceException(
        service.id, errors.NO_DRV_ERROR, "Service has no driver assigned"
    )
