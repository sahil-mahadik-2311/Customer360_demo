
@router.get("/failed-messages", response_model=int)
async def failed_messages(
    emp: emp_dependency,
    db: db_dependency,
    kpi: kpi_dependency
):
    if emp is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication Failed")

    logger.info("failed-messages endpoint called")
    return kpi.get_failed_messages()
